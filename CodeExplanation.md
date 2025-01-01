# ChordScribe - Keyboard Layout Optimization Project

## Overview

ChordScribe is a project focused on creating a more efficient typing ecosystem by optimizing keyboard layouts. The project analyzes and compares different keyboard layouts (like QWERTY, Dvorak, Colemak, and custom layouts) to determine their efficiency based on various metrics.

## Core Components

### 1. Layout System

- Defined in `Layout Optimization/src/layout.js`
- Handles the representation and parsing of keyboard layouts
- Converts layouts into metrics for analysis
- Supports both normal and shifted characters

### 2. Configuration (`src/config.js`)

Key parameters and measurements:

- `EFFORT_LIMIT`: Maximum effort threshold for typing analysis
- `SAME_FINGER_PENALTY`: Penalty multiplier for using the same finger consecutively
- `SAME_HAND_PENALTY`: Penalty multiplier for using the same hand consecutively
- Detailed mappings for:
  - Key coordinates
  - Finger travel distances
  - Hand movement efforts
  - Row numbers
  - Finger assignments

### 3. Analysis Engine (`src/runner.js`)

Measures typing efficiency by:

- Tracking finger movements and distances
- Calculating typing effort
- Analyzing overheads from:
  - Same finger usage
  - Same hand usage
  - Shift key usage
- Collecting statistics on finger and hand usage

### 4. Layout Comparison System (`src/compare.js`)

- Compares different keyboard layouts
- Generates statistics for:
  - Typing speed (positions reached)
  - Effort per symbol
  - Distance per symbol
  - Hand usage balance
  - Finger usage distribution
  - Various overhead metrics

### 5. User Interface (`src/ui.js`)

Built using blessed/blessed-contrib libraries, featuring:

- Layout comparison table
- Keyboard details display
- Analysis progress tracking
- Genetic algorithm information
- Performance charts and gauges

## Key Metrics

The system evaluates layouts based on:

1. **Effort**: Energy required for typing
2. **Distance**: Physical distance fingers must travel
3. **Overheads**:
   - Same finger usage penalties
   - Same hand usage penalties
   - Shifting penalties
4. **Balance**:
   - Hand usage symmetry
   - Finger load distribution
   - Row usage patterns

## Keyboard Layouts Compared

The system compares several keyboard layouts, each designed with different optimization goals:

### 1. QWERTY

- The standard keyboard layout used worldwide
- Designed in the 1870s for mechanical typewriters
- Layout arranged to prevent key jamming in mechanical typewriters
- Not optimized for typing efficiency or ergonomics
- Used as the baseline for comparisons

### 2. Dvorak

- Developed by August Dvorak in the 1930s
- Designed for efficient and ergonomic typing
- Places most common letters on the home row
- Alternates between hands frequently for faster typing
- Layout:
  - All vowels on the left home row
  - Most common consonants on the right home row
  - Less frequent letters on bottom row

### 3. Colemak

- Modern layout created in 2006 by Shai Coleman
- Designed to be easier to learn than Dvorak
- Keeps many QWERTY shortcuts (Z,X,C,V) in same position
- 17 keys different from QWERTY (vs. 33 in Dvorak)
- Focuses on home row usage and hand alternation
- Popular among programmers and power users

### 4. Workman

- Created by OJ Bucao in 2010
- Focuses on reducing finger travel distance
- Designed with modern typing patterns in mind
- Emphasizes reducing lateral finger movements
- Places common punctuation marks in easier-to-reach positions

### 5. Halmak Variations

- Custom experimental layouts in the project
- Multiple versions (Halmak1, Halmak2, Halmak21, Halmak22)
- Generated using genetic algorithms
- Optimized based on:
  - Finger travel distance
  - Hand alternation
  - Common letter combinations
  - Typing effort metrics

### 6. QWERTZ (German)

- Standard keyboard layout used in German-speaking countries
- Similar to QWERTY but with several key differences:
  - Z and Y positions are swapped (hence QWERTZ name)
  - Special characters for German language (ä, ö, ü, ß)
  - Different symbol placements for European standards
- Optimized for German language characteristics
- Additional features:
  - Umlauts accessible via dedicated keys
  - Extra characters for European languages
  - Common German letter combinations considered
- Layout differences from QWERTY:
  - Y is on the right side (easier access for German words)
  - Special characters positioned for German typing efficiency
  - Modified punctuation mark positions
  - Additional AltGr key combinations for extended characters

Each layout is evaluated based on:

- Overall typing efficiency
- Finger movement patterns
- Hand usage balance
- Learning curve difficulty
- Compatibility with modern typing needs

## Layout Optimization

The project includes:

- Multiple preset layouts (QWERTY, Dvorak, Colemak, Workman)
- Custom layout definitions (Halmak variations)
- Testing framework for layout comparison
- Genetic algorithm components for layout optimization

## Technical Implementation

- Written in JavaScript/Node.js
- Uses modern ES6+ features
- Includes comprehensive test suite
- Modular architecture for easy extension
- Performance-optimized analysis algorithms

## Running the Application

### Prerequisites

- Node.js installed on your system
- npm (Node Package Manager)

### Installation Steps

1. Clone the repository
2. Navigate to the Layout Optimization directory:
   ```bash
   cd Layout\ Optimization/
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

### Running the Application

There are two main ways to run the application:

1. Start the main application (with UI):

   ```bash
   npm start
   ```

   This will launch the interactive UI where you can compare different layouts and see the analysis in real-time.

2. Run the comparison tests:
   ```bash
   npm test
   ```
   This will run the automated tests comparing different keyboard layouts and output the results.

### Understanding the Output

- The UI will show a table comparing different layouts with the following metrics:

  1. **Score**: Overall efficiency score of the layout

     - Lower scores indicate better efficiency
     - Calculated based on combined metrics of effort, distance, and penalties
     - Represents the total energy cost of typing

  2. **Dist. (Distance)**: Average finger travel distance

     - Measured in arbitrary units (based on key size)
     - Lower distances indicate less finger movement
     - Represents physical effort required for typing

  3. **vs.Workman**: Comparison against the Workman layout

     - Shows percentage difference in efficiency
     - Positive numbers indicate better performance than Workman
     - Negative numbers indicate worse performance than Workman

  4. **vs.QWERTY**: Comparison against the QWERTY layout
     - Shows percentage difference in efficiency
     - Positive numbers indicate better performance than QWERTY
     - Negative numbers indicate worse performance than QWERTY
     - QWERTY is used as a baseline as it's the most common layout

- Each layout's additional metrics will be displayed:
  - Typing speed
  - Effort per symbol
  - Hand/finger usage statistics
- The charts will visualize the performance differences
- The genetic algorithm progress (if enabled) will be shown in real-time

## Adding New Keyboard Layouts

You can add your own custom keyboard layouts to the system for analysis and comparison.

### Layout Definition Format

New layouts should be defined using the following format:

```javascript
const NewLayout = new Layout(
  "LayoutName",
  `
\` 1 2 3 4 5 6 7 8 9 0 - =
~ ! @ # $ % ^ & * ( ) _ +
  q w e r t y u i o p [ ] \\
  Q W E R T Y U I O P { } |
  a s d f g h j k l ; ' \\n
  A S D F G H J K L : " \\n
   z x c v b n m , . /
   Z X C V B N M < > ?
`
);
```

### Steps to Add a New Layout

1. Open `Layout Optimization/src/presets.js` or create a new file for your layouts
2. Define your new layout using the format above
3. Ensure your layout includes:
   - All standard keys (letters, numbers, symbols)
   - Both lowercase and uppercase characters
   - Proper spacing and alignment
   - Special characters (\\n for newline, etc.)

### Layout Rules

- Each row must be properly aligned
- Special characters must be escaped (\\, \\n)
- Layout must include:
  - Number row with symbols
  - Three letter rows
  - Both normal and shifted characters
- Maintain consistent spacing between keys

### Example Implementation

```javascript
// In Layout Optimization/src/presets.js or your new file

const MyCustomLayout = new Layout(
  "MyLayout",
  `
\` 1 2 3 4 5 6 7 8 9 0 - =
~ ! @ # $ % ^ & * ( ) _ +
  n e i o p k d h c v [ ] \\
  N E I O P K D H C V { } |
  a t r s g y u l m f ' \\n
  A T R S G Y U L M F " \\n
   z w x b j q . , ; /
   Z W X B J Q > < : ?
`
);

// Add to LAYOUTS array in compare.js
const LAYOUTS = [QWERTY, Workman, Colemak, Dvorak, MyCustomLayout];
```

### Testing Your Layout

1. After adding your layout, run the comparison tests:

   ```bash
   npm test
   ```

2. Check the results to see how your layout performs against others:
   - Overall efficiency score
   - Distance metrics
   - Hand/finger usage balance
   - Comparison with standard layouts

### Best Practices

1. Consider these factors when designing your layout:

   - Frequently used characters should be on home row
   - Balance usage between hands
   - Minimize same-finger and same-hand sequences
   - Keep common shortcuts accessible
   - Consider ergonomic finger movement patterns

2. Document your layout's design principles:
   - Key placement rationale
   - Optimization goals
   - Target use cases
   - Expected advantages

## Purpose

The project aims to:

1. Analyze keyboard layout efficiency
2. Compare different layout designs
3. Optimize typing patterns
4. Reduce typing strain and effort
5. Improve typing speed and comfort

This system provides a scientific approach to keyboard layout design, using quantitative metrics to measure and optimize typing efficiency.

## Code Changes for German Keyboard Implementation

### 1. File Structure Changes

New files added:

```
Layout Optimization/
├── text/
│   ├── englishText.txt    # English testing text
│   └── germanText.txt     # German testing text with umlauts
├── test/
│   ├── helper.js          # Modified to support multiple languages
│   └── qwertz_test.js     # New German layout tests
└── src/
    ├── presets.js         # Added QWERTZ layout
    └── compare.js         # Modified for dual-language testing
```

### 2. Layout Definition (`src/presets.js`)

Added QWERTZ layout definition:

```javascript
const QWERTZ = new Layout(
  "QWERTZ",
  `
  \` 1 2 3 4 5 6 7 8 9 0 ß ´
  ° ! " § $ % & / ( ) = ? \`
    q w e r t z u i o p ü + \\
    Q W E R T Z U I O P Ü * |
    a s d f g h j k l ö ä \\n
    A S D F G H J K L Ö Ä \\n
     y x c v b n m , . -
     Y X C V B N M ; : _
  `
);
```

Key changes:

- Added German special characters (ä, ö, ü, ß)
- Swapped Z and Y positions
- Modified symbol placements for German standards
- Added proper escape sequences (\\n, \\, |)

### 3. Test Helper Modifications (`test/helper.js`)

Updated to support multiple languages:

```javascript
// Load both English and German text fixtures
global.TEXT_FIXTURE_EN = `...English text...`;

global.TEXT_FIXTURE_DE = fs.readFileSync(
  path.join(__dirname, "../text/germanText.txt"),
  "utf8"
);

// Default to English text for backward compatibility
global.TEXT_FIXTURE = global.TEXT_FIXTURE_EN;
```

Changes:

- Added German text fixture loading
- Maintained backward compatibility
- Separated language-specific test data

### 4. Comparison Script Changes (`src/compare.js`)

Modified to test both languages:

```javascript
// Load both English and German text
const englishText = fs.readFileSync(...);
const germanText = fs.readFileSync(...);

// Test English layouts
const englishResults = [QWERTY, Workman, Colemak, Dvorak]
  .map(layout => {...});

// Test German layouts
const germanResults = [QWERTZ, QWERTY]
  .map(layout => {...});

// Combine and sort results
const allResults = [...englishResults, ...germanResults];
```

Key changes:

- Separate runners for each language
- Language-specific layout testing
- Combined results for comparison
- Enhanced output formatting

### 5. Testing Implementation

New test file for German layout (`test/qwertz_test.js`):

```javascript
describe("QWERTZ Layout with German Text", () => {
  const runner = new Runner(global.TEXT_FIXTURE_DE, {
    effortLimit: 2000,
    sameHandPenalty: 0.5,
    sameFingerPenalty: 5,
  });

  it("performs better than QWERTY for German text", () => {
    // Test implementation
  });
});
```

Test features:

- German-specific text testing
- QWERTZ vs QWERTY comparison
- Special character handling
- Ergonomic metrics for German typing

### 6. Running the Tests

To test both English and German layouts:

```bash
npm test
```

Output includes:

- English layout performance metrics
- German layout performance metrics
- Comparative analysis between layouts
- Detailed statistics for each layout

### 7. Code Organization

The implementation follows these principles:

- Clear separation of language-specific components
- Maintainable and extensible structure
- Backward compatibility with existing tests
- Proper error handling for special characters

### 8. Future Code Considerations

Areas for potential code enhancement:

- Additional language support framework
- More comprehensive testing metrics
- Regional layout variants
- Extended character set support
- Performance optimization for large texts
