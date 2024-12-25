import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import aiofiles
import ssl
import argparse

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
import zipfile
import os
import re
from pathlib import Path
import logging
from typing import List, Set, Tuple, Optional
from urllib.parse import urljoin, parse_qs, urlparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GutenbergHarvester:
    def __init__(self, output_dir: str = "gutenberg_books"):
        print("\n[INIT] Initializing GutenbergHarvester...")
        self.base_url = "https://www.gutenberg.org/robot/harvest"
        self.mirror_urls = [
            "https://www.gutenberg.org/files",
            "http://aleph.gutenberg.org",
            "http://www.gutenberg.org/cache/epub"
        ]
        self.download_dir = Path("downloads")
        self.extracted_dir = Path("extracted")
        self.processed_dir = Path(output_dir)
        self.processed_ids: Set[str] = set()
        self.failed_downloads: Set[str] = set()
        self.corrupt_files: Set[str] = set()
        self.semaphore = asyncio.Semaphore(10)
        
        # Create necessary directories
        for directory in [self.download_dir, self.extracted_dir, self.processed_dir]:
            directory.mkdir(exist_ok=True)
            print(f"[INIT] Created directory: {directory}")
        print("[INIT] Initialization complete\n")

    def generate_mirror_urls(self, book_id: str) -> List[str]:
        """Generate alternative URLs for different mirrors."""
        print(f"[MIRRORS] Generating mirror URLs for book ID: {book_id}")
        urls = []
        id_parts = "/".join(book_id[i:i+1] for i in range(0, len(book_id)-1))
        
        for mirror in self.mirror_urls:
            # Standard format: /files/1/2/3/1234/1234.zip
            urls.append(f"{mirror}/{id_parts}/{book_id}/{book_id}.zip")
            # Alternative format: /cache/epub/1234/pg1234.txt.utf8.zip
            urls.append(f"{mirror}/{book_id}/pg{book_id}.txt.utf8.zip")
        
        return urls

    async def validate_zip_file(self, zip_path: Path, delete_if_invalid: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Validate ZIP file integrity and content.
        Returns (is_valid, error_message)
        """
        print(f"[VALIDATE] Checking ZIP file: {zip_path}")
        try:
            with zipfile.ZipFile(zip_path) as zf:
                # Test ZIP file integrity
                test_result = zf.testzip()
                if test_result is not None:
                    print(f"[VALIDATE] ❌ Corrupt ZIP detected: {zip_path}")
                    error_msg = f"Corrupt ZIP file {zip_path}: First bad file is {test_result}"
                    if delete_if_invalid and zip_path.exists():
                        zip_path.unlink()
                    return False, error_msg
                
                # Verify content
                txt_files = [f for f in zf.namelist() if f.endswith('.txt')]
                if not txt_files:
                    print(f"[VALIDATE] ❌ No text files found in: {zip_path}")
                    error_msg = f"No text files found in {zip_path}"
                    if delete_if_invalid and zip_path.exists():
                        zip_path.unlink()
                    return False, error_msg
                
                # Check file sizes
                for txt_file in txt_files:
                    if zf.getinfo(txt_file).file_size == 0:
                        print(f"[VALIDATE] ❌ Empty text file found: {txt_file}")
                        error_msg = f"Empty text file found in {zip_path}: {txt_file}"
                        if delete_if_invalid and zip_path.exists():
                            zip_path.unlink()
                        return False, error_msg
                
                print(f"[VALIDATE] ✅ ZIP file valid: {zip_path}")
                return True, None
                
        except zipfile.BadZipFile:
            print(f"[VALIDATE] ❌ Invalid ZIP file: {zip_path}")
            error_msg = f"Invalid ZIP file: {zip_path}"
            if delete_if_invalid and zip_path.exists():
                zip_path.unlink()
            return False, error_msg
        except Exception as e:
            print(f"[VALIDATE] ❌ Error validating ZIP: {zip_path}, Error: {e}")
            error_msg = f"Error validating ZIP file {zip_path}: {e}"
            if delete_if_invalid and zip_path.exists():
                zip_path.unlink()
            return False, error_msg

    async def download_with_mirrors(self, url: str, zip_path: Path) -> Tuple[bool, Optional[str]]:
        """Attempt to download from primary URL and fall back to mirrors if needed."""
        book_id = url.split('/')[-2]
        urls_to_try = [url] + self.generate_mirror_urls(book_id)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        for attempt_url in urls_to_try:
            print(f"[DOWNLOAD] Attempting download from: {attempt_url}")
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                    async with session.get(attempt_url, headers=headers, timeout=30) as response:
                        if response.status == 404:
                            print(f"[DOWNLOAD] 404 Not found: {attempt_url}")
                            continue
                        
                        if response.status != 200:
                            print(f"[DOWNLOAD] Status {response.status}: {attempt_url}")
                            continue
                        
                        content = await response.read()
                        if len(content) < 100:  # Basic size check
                            print(f"[DOWNLOAD] Content too small: {attempt_url}")
                            continue
                            
                        async with aiofiles.open(zip_path, 'wb') as f:
                            await f.write(content)
                        
                        print(f"[DOWNLOAD] ✅ Successfully downloaded: {zip_path}")
                        
                        # Validate the downloaded file
                        is_valid, error_msg = await self.validate_zip_file(zip_path)
                        if is_valid:
                            return True, None
                        else:
                            if zip_path.exists():
                                zip_path.unlink()
                            continue
                            
            except asyncio.TimeoutError:
                print(f"[DOWNLOAD] Timeout: {attempt_url}")
                continue
            except Exception as e:
                print(f"[DOWNLOAD] Error: {attempt_url}, {str(e)}")
                continue
        
        print(f"[DOWNLOAD] ❌ All download attempts failed for book {book_id}")
        return False, f"All download attempts failed for book {book_id}"

    async def download_book(self, url: str) -> bool:
        """Download a single book ZIP file with mirror fallback and validation."""
        book_id = url.split('/')[-2]
        if book_id in self.processed_ids or book_id in self.failed_downloads:
            print(f"[BOOK] Skipping already processed/failed book: {book_id}")
            return False

        zip_path = self.download_dir / f"{book_id}.zip"
        max_retries = 3
        retry_count = 0
        
        async with self.semaphore:
            while retry_count < max_retries:
                print(f"[BOOK] Download attempt {retry_count + 1}/{max_retries} for book {book_id}")
                success, error_msg = await self.download_with_mirrors(url, zip_path)
                
                if success:
                    print(f"[BOOK] ✅ Successfully downloaded book: {book_id}")
                    return True
                
                retry_count += 1
                if retry_count < max_retries:
                    print(f"[BOOK] Retrying download for book: {book_id}")
                    await asyncio.sleep(1)  # Wait before retrying
            
            if error_msg:
                logging.error(error_msg)
            self.failed_downloads.add(book_id)
            print(f"[BOOK] ❌ Failed to download book: {book_id}")
            return False

    async def process_book(self, zip_path: Path) -> None:
        """Extract and process a book from its ZIP file with enhanced validation."""
        book_id = zip_path.stem
        print(f"\n[PROCESS] Processing book: {book_id}")
        
        try:
            # Validate ZIP file before processing
            is_valid, error_msg = await self.validate_zip_file(zip_path)
            if not is_valid:
                if error_msg:
                    logging.error(error_msg)
                self.failed_downloads.add(book_id)
                return

            print(f"[PROCESS] Extracting files from: {zip_path}")
            with zipfile.ZipFile(zip_path) as zf:
                txt_files = [f for f in zf.namelist() if f.endswith('.txt')]
                zf.extractall(self.extracted_dir)
            
            processed_any = False
            for txt_file in txt_files:
                print(f"[PROCESS] Processing text file: {txt_file}")
                extracted_path = self.extracted_dir / txt_file
                try:
                    async with aiofiles.open(extracted_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = await f.read()
                    
                    if not content.strip():
                        print(f"[PROCESS] ⚠️ Empty content in {txt_file}")
                        continue
                    
                    processed_content = self.process_text(content)
                    if not processed_content.strip():
                        print(f"[PROCESS] ⚠️ Empty processed content for {txt_file}")
                        continue
                    
                    output_path = self.processed_dir / f"{book_id}.txt"
                    async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                        await f.write(processed_content)
                    
                    print(f"[PROCESS] ✅ Successfully processed: {txt_file}")
                    processed_any = True
                    
                except Exception as e:
                    print(f"[PROCESS] ❌ Error processing text file {txt_file}: {e}")
                finally:
                    if extracted_path.exists():
                        extracted_path.unlink()
            
            if processed_any:
                self.processed_ids.add(book_id)
                print(f"[PROCESS] ✅ Successfully processed book: {book_id}")
            else:
                self.failed_downloads.add(book_id)
                print(f"[PROCESS] ❌ Failed to process book: {book_id}")
            
            if zip_path.exists():
                zip_path.unlink()
            
        except Exception as e:
            print(f"[PROCESS] ❌ Error processing {zip_path}: {e}")
            self.failed_downloads.add(book_id)
            if zip_path.exists():
                zip_path.unlink()

    def process_text(self, text: str) -> str:
        """Process text content with enhanced error handling."""
        try:
            # Find and remove header
            start_markers = [
                "*** START OF THIS PROJECT GUTENBERG",
                "*** START OF THE PROJECT GUTENBERG",
            ]
            end_markers = [
                "*** END OF THIS PROJECT GUTENBERG",
                "*** END OF THE PROJECT GUTENBERG",
            ]
            
            header_end = -1
            for marker in start_markers:
                pos = text.find(marker)
                if pos != -1:
                    header_end = text.find('\n', pos) + 1
                    break
            
            if header_end != -1:
                text = text[header_end:]
            
            # Remove footer
            footer_start = len(text)
            for marker in end_markers:
                pos = text.find(marker)
                if pos != -1:
                    footer_start = pos
                    break
            
            text = text[:footer_start]
            
            # Remove license information
            license_markers = [
                "End of the Project Gutenberg",
                "End of Project Gutenberg",
                "*** END OF THIS PROJECT GUTENBERG",
                "*** END OF THE PROJECT GUTENBERG"
            ]
            
            for marker in license_markers:
                pos = text.rfind(marker)
                if pos != -1:
                    text = text[:pos].strip()
            
            # Clean up extra whitespace
            return re.sub(r'\n{3,}', '\n\n', text.strip())
        except Exception as e:
            print(f"[TEXT] ❌ Error processing text content: {e}")
            return text

    async def get_page_content(self, url: str, params: dict = None) -> Tuple[List[str], Optional[str]]:
        """Fetch book download links and next page link from the harvest page."""
        print(f"\n[PAGE] Fetching content from: {url}")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        print(f"[PAGE] ❌ Failed to fetch page: {url} (Status: {response.status})")
                        return [], None
                    
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    links = [a['href'] for a in soup.find_all('a', href=True) 
                            if a['href'].endswith('.zip')]
                    print(f"[PAGE] Found {len(links)} book links")
                    
                    next_link = soup.find('a', string='Next Page')
                    next_url = None
                    if next_link and 'href' in next_link.attrs:
                        next_url = urljoin(self.base_url, next_link['href'])
                        parsed_url = urlparse(next_url)
                        query_params = parse_qs(parsed_url.query)
                        if 'filetypes[]' not in query_params:
                            next_url = f"{next_url}&filetypes[]=txt&langs[]=de"
                        print(f"[PAGE] Found next page: {next_url}")
                    else:
                        print("[PAGE] No next page found")
                    
                    return links, next_url
            except asyncio.TimeoutError:
                print(f"[PAGE] ❌ Timeout while fetching page: {url}")
                return [], None
            except Exception as e:
                print(f"[PAGE] ❌ Error fetching page {url}: {e}")
                return [], None

    async def harvest_books(self):
        """Main harvesting method with enhanced error handling and reporting."""
        print("\n[HARVEST] Starting book harvesting process...")
        current_url = self.base_url
        params = {'filetypes[]': 'txt', 'langs[]': 'de'}
        
        try:
            while True:
                print(f"\n[HARVEST] Processing page: {current_url}")
                links, next_url = await self.get_page_content(current_url, params)
                
                if not links:
                    print("[HARVEST] No more books found.")
                    break
                
                print(f"[HARVEST] Downloading {len(links)} books...")
                download_tasks = [self.download_book(link) for link in links]
                download_results = await asyncio.gather(*download_tasks, return_exceptions=True)
                
                zip_files = list(self.download_dir.glob('*.zip'))
                print(f"[HARVEST] Processing {len(zip_files)} downloaded books...")
                process_tasks = [self.process_book(zip_path) for zip_path in zip_files]
                await asyncio.gather(*process_tasks, return_exceptions=True)
                
                if not next_url:
                    print("[HARVEST] No next page link found.")
                    break
                
                current_url = next_url
                params = None
                print("[HARVEST] Waiting before fetching next page...")
                await asyncio.sleep(1)
            
            # Final report
            print("\n[HARVEST] 📊 Final Report:")
            print(f"✅ Successfully processed: {len(self.processed_ids)} books")
            if self.failed_downloads:
                print(f"❌ Failed to process: {len(self.failed_downloads)} books")
                print(f"Failed book IDs: {sorted(self.failed_downloads)}")
                
        except Exception as e:
            print(f"[HARVEST] ❌ Fatal error in harvest_books: {e}")
            raise

    def count_downloaded_books(self) -> int:
        """Count the number of books in the output directory."""
        try:
            book_count = len(list(self.processed_dir.glob('*.txt')))
            print(f"\n[COUNT] 📚 Found {book_count} books in {self.processed_dir}")
            return book_count
        except Exception as e:
            print(f"[COUNT] ❌ Error counting books: {e}")
            return 0

async def main():
    print("\n🚀 Starting Gutenberg Book Harvester")
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Gutenberg Book Harvester')
    parser.add_argument('--count-only', action='store_true', 
                       help='Only count existing books without downloading new ones')
    args = parser.parse_args()
    
    harvester = GutenbergHarvester()
    
    if args.count_only:
        harvester.count_downloaded_books()
    else:
        await harvester.harvest_books()
        print(f"\nFinal book count: {harvester.count_downloaded_books()}")
    
    print("\n✨ Process complete")

if __name__ == "__main__":
    asyncio.run(main())
