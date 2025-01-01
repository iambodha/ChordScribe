/**
 * Imports data and builds the library
 */

const fs = require("fs");
const path = require("path");

// Recursively find all files with the specified extension in the given directory
function getAllFilesWithExtension(dirPath, extension) {
  let filesWithExtension = [];
  const files = fs.readdirSync(dirPath);

  files.forEach((file) => {
    const filePath = path.join(dirPath, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      filesWithExtension = filesWithExtension.concat(getAllFilesWithExtension(filePath, extension));
    } else if (path.extname(file) === extension) {
      filesWithExtension.push(filePath);
    }
  });

  return filesWithExtension;
}

// Read and concatenate all .md files in the current directory and its subdirectories
try {
  const mdFiles = getAllFilesWithExtension('.', '.md');
  const docs = exports.docs = mdFiles
    .map((filePath) => fs.readFileSync(filePath, 'utf8'))
    .join("\n")
    .replace(/\n```[\s\S]+?\n```\n/g, "");  // Optional regex to remove code blocks
} catch (error) {
  console.error("Error reading markdown files:", error);
}

// Read and concatenate all .txt files in the "text" directory
try {
  const text = exports.text = fs.readdirSync("text")
    .filter(filename => /\.txt$/.test(filename))
    .map(filename => fs.readFileSync(`text/${filename}`, 'utf8'))
    .join("\n\n");
} catch (error) {
  console.error("Error reading text files:", error);
}

// Read and concatenate all .js files in the current directory and its subdirectories
try {
  const jsFiles = getAllFilesWithExtension('.', '.js');
  const code = exports.code = jsFiles
    .map((filePath) => fs.readFileSync(filePath, 'utf8'))
    .join("\n");
} catch (error) {
  console.error("Error reading JavaScript files:", error);
}

// http://www3.nd.edu/~busiforc/handouts/cryptography/Letter%20Frequencies.html
const POPULAR_TRIGRAMS = {
  the: 59623899,
  and: 27088636,
  ing: 19494469,
  her: 13977786,
  hat: 11059185,
  his: 10141992,
  tha: 10088372,
  ere: 9527535,
  for: 9438784,
  ent: 9020688,
  ion: 8607405,
  ter: 7836576,
  was: 7826182,
  you: 7430619,
  ith: 7329285,
  ver: 7320472,
  all: 7184955,
  wit: 6752112,
  thi: 6709729,
  tio: 6425262,
};

const POPULAR_BIGRAMS = {
  th: 92535489,
  he: 87741289,
  in: 54433847,
  er: 51910883,
  an: 51015163,
  re: 41694599,
  nd: 37466077,
  on: 33802063,
  en: 32967758,
  at: 31830493,
  ou: 30637892,
  ed: 30406590,
  ha: 30381856,
  to: 27877259,
  or: 27434858,
  it: 27048699,
  is: 26452510,
  hi: 26033632,
  es: 26033602,
  ng: 25106109,
};

const trigrams = exports.trigrams = generate_text_from(POPULAR_TRIGRAMS);
const bigrams  = exports.bigrams  = generate_text_from(POPULAR_BIGRAMS);

function generate_text_from(dictionary) {
  let total = 0;

  for (let key in dictionary) {
    total += dictionary[key];
  }

  let tokens = [];
  for (let key in dictionary) {
    const percent = Math.round(dictionary[key] / total * 100);

    tokens.push(repeat(key, percent));
    tokens.push(repeat(titleize(key), percent));
  }

  return tokens.join(" ");
}

function repeat(string, times) {
  let result = [];
  for (let i = 0; i < times; i++) {
    result.push(string);
  }
  return result.join(" ");
}

function titleize(str) {
  return str[0].toUpperCase() + str.substr(1);
}
