import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import aiofiles
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
        
        for directory in [self.download_dir, self.extracted_dir, self.processed_dir]:
            directory.mkdir(exist_ok=True)

    def generate_mirror_urls(self, book_id: str) -> List[str]:
        urls = []
        id_parts = "/".join(book_id[i:i+1] for i in range(0, len(book_id)-1))
        
        for mirror in self.mirror_urls:
            urls.append(f"{mirror}/{id_parts}/{book_id}/{book_id}.zip")
            urls.append(f"{mirror}/{book_id}/pg{book_id}.txt.utf8.zip")
        
        return urls

    async def validate_zip_file(self, zip_path: Path, delete_if_invalid: bool = True) -> Tuple[bool, Optional[str]]:
        try:
            with zipfile.ZipFile(zip_path) as zf:
                test_result = zf.testzip()
                if test_result is not None:
                    error_msg = f"Corrupt ZIP file {zip_path}: First bad file is {test_result}"
                    if delete_if_invalid and zip_path.exists():
                        zip_path.unlink()
                    return False, error_msg
                
                txt_files = [f for f in zf.namelist() if f.endswith('.txt')]
                if not txt_files:
                    error_msg = f"No text files found in {zip_path}"
                    if delete_if_invalid and zip_path.exists():
                        zip_path.unlink()
                    return False, error_msg
                
                for txt_file in txt_files:
                    if zf.getinfo(txt_file).file_size == 0:
                        error_msg = f"Empty text file found in {zip_path}: {txt_file}"
                        if delete_if_invalid and zip_path.exists():
                            zip_path.unlink()
                        return False, error_msg
                
                return True, None
                
        except zipfile.BadZipFile:
            error_msg = f"Invalid ZIP file: {zip_path}"
            if delete_if_invalid and zip_path.exists():
                zip_path.unlink()
            return False, error_msg
        except Exception as e:
            error_msg = f"Error validating ZIP file {zip_path}: {e}"
            if delete_if_invalid and zip_path.exists():
                zip_path.unlink()
            return False, error_msg

    async def download_with_mirrors(self, url: str, zip_path: Path) -> Tuple[bool, Optional[str]]:
        book_id = url.split('/')[-2]
        urls_to_try = [url] + self.generate_mirror_urls(book_id)
        
        for attempt_url in urls_to_try:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attempt_url, timeout=30) as response:
                        if response.status == 404:
                            continue
                        
                        if response.status != 200:
                            continue
                        
                        content = await response.read()
                        if len(content) < 100:
                            continue
                            
                        async with aiofiles.open(zip_path, 'wb') as f:
                            await f.write(content)
                        
                        is_valid, error_msg = await self.validate_zip_file(zip_path)
                        if is_valid:
                            return True, None
                        else:
                            if zip_path.exists():
                                zip_path.unlink()
                            continue
                            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                continue
        
        return False, f"All download attempts failed for book {book_id}"

    async def download_book(self, url: str) -> bool:
        book_id = url.split('/')[-2]
        if book_id in self.processed_ids or book_id in self.failed_downloads:
            return False

        zip_path = self.download_dir / f"{book_id}.zip"
        max_retries = 3
        retry_count = 0
        
        async with self.semaphore:
            while retry_count < max_retries:
                success, error_msg = await self.download_with_mirrors(url, zip_path)
                
                if success:
                    return True
                
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)
            
            if error_msg:
                logging.error(error_msg)
            self.failed_downloads.add(book_id)
            return False

    async def process_book(self, zip_path: Path) -> None:
        book_id = zip_path.stem
        
        try:
            is_valid, error_msg = await self.validate_zip_file(zip_path)
            if not is_valid:
                if error_msg:
                    logging.error(error_msg)
                self.failed_downloads.add(book_id)
                return

            with zipfile.ZipFile(zip_path) as zf:
                txt_files = [f for f in zf.namelist() if f.endswith('.txt')]
                zf.extractall(self.extracted_dir)
            
            processed_any = False
            for txt_file in txt_files:
                extracted_path = self.extracted_dir / txt_file
                try:
                    async with aiofiles.open(extracted_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = await f.read()
                    
                    if not content.strip():
                        logging.warning(f"Empty content in {txt_file}")
                        continue
                    
                    processed_content = self.process_text(content)
                    if not processed_content.strip():
                        logging.warning(f"Empty processed content for {txt_file}")
                        continue
                    
                    output_path = self.processed_dir / f"{book_id}.txt"
                    async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                        await f.write(processed_content)
                    
                    processed_any = True
                    
                except Exception as e:
                    logging.error(f"Error processing text file {txt_file}: {e}")
                finally:
                    if extracted_path.exists():
                        extracted_path.unlink()
            
            if processed_any:
                self.processed_ids.add(book_id)
            else:
                self.failed_downloads.add(book_id)
            
            if zip_path.exists():
                zip_path.unlink()
            
        except Exception as e:
            logging.error(f"Error processing {zip_path}: {e}")
            self.failed_downloads.add(book_id)
            if zip_path.exists():
                zip_path.unlink()

    def process_text(self, text: str) -> str:
        try:
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
            
            footer_start = len(text)
            for marker in end_markers:
                pos = text.find(marker)
                if pos != -1:
                    footer_start = pos
                    break
            
            text = text[:footer_start]
            
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
            
            return re.sub(r'\n{3,}', '\n\n', text.strip())
        except Exception as e:
            logging.error(f"Error processing text content: {e}")
            return text

    async def get_page_content(self, url: str, params: dict = None) -> Tuple[List[str], Optional[str]]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status != 200:
                        logging.error(f"Failed to fetch page: {url} (Status: {response.status})")
                        return [], None
                    
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    links = [a['href'] for a in soup.find_all('a', href=True) 
                            if a['href'].endswith('.zip')]
                    
                    next_link = soup.find('a', string='Next Page')
                    next_url = None
                    if next_link and 'href' in next_link.attrs:
                        next_url = urljoin(self.base_url, next_link['href'])
                        parsed_url = urlparse(next_url)
                        query_params = parse_qs(parsed_url.query)
                        if 'filetypes[]' not in query_params:
                            next_url = f"{next_url}&filetypes[]=txt&langs[]=en"
                    
                    return links, next_url
            except asyncio.TimeoutError:
                logging.error(f"Timeout while fetching page: {url}")
                return [], None
            except Exception as e:
                logging.error(f"Error fetching page {url}: {e}")
                return [], None

    async def harvest_books(self):
        current_url = self.base_url
        params = {'filetypes[]': 'txt', 'langs[]': 'en'}
        
        try:
            while True:
                logging.info(f"Fetching links from: {current_url}")
                links, next_url = await self.get_page_content(current_url, params)
                
                if not links:
                    logging.info("No more books found.")
                    break
                
                download_tasks = [self.download_book(link) for link in links]
                download_results = await asyncio.gather(*download_tasks, return_exceptions=True)
                
                zip_files = list(self.download_dir.glob('*.zip'))
                process_tasks = [self.process_book(zip_path) for zip_path in zip_files]
                await asyncio.gather(*process_tasks, return_exceptions=True)
                
                if not next_url:
                    logging.info("No next page link found.")
                    break
                
                current_url = next_url
                params = None
                await asyncio.sleep(1)
            
            logging.info(f"Harvest complete. Processed {len(self.processed_ids)} books successfully.")
            if self.failed_downloads:
                logging.warning(f"Failed to process {len(self.failed_downloads)} books: {sorted(self.failed_downloads)}")
                
        except Exception as e:
            logging.error(f"Fatal error in harvest_books: {e}")
            raise

async def main():
    harvester = GutenbergHarvester()
    await harvester.harvest_books()

if __name__ == "__main__":
    asyncio.run(main())
