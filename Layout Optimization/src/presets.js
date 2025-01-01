/**
 * Known preset layouts to measure against
 */
const Layout = require("./layout");

// Define all layouts
const QWERTY = new Layout(
  "QWERTY",
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

const Workman = new Layout(
  "Workman",
  `
  \` 1 2 3 4 5 6 7 8 9 0 - =
   ~ ! @ # $ % ^ & * ( ) _ +
     q d r w b j f u p ; [ ] \\
     Q D R W B J F U P : { } |
     a s h t g y n e o i ' \\n
     A S H T G Y N E O I " \\n
      z x m c v k l , . /
      Z X M C V K L < > ?
`
);

const Colemak = new Layout(
  "Colemak",
  `
  \` 1 2 3 4 5 6 7 8 9 0 - =
   ~ ! @ # $ % ^ & * ( ) _ +
     q w f p g j l u y ; [ ] \\
     Q W F P G J L U Y : { } |
     a r s t d h n e i o ' \\n
     A R S T D H N E I O " \\n
      z x c v b k m , . /
      Z X C V B K M < > ?
`
);

const Dvorak = new Layout(
  "Dvorak",
  `
  \` 1 2 3 4 5 6 7 8 9 0 [ ]
   ~ ! @ # $ % ^ & * ( ) { }
     ' , . p y f g c r l / = \\
     " < > P Y F G C R L ? + |
     a o e u i d h t n s - \\n
     A O E U I D H T N S _ \\n
      ; q j k x b m w v z
      : Q J K X B M W V Z
`
);

// Export all layouts
module.exports = {
  QWERTY,
  QWERTZ,
  Workman,
  Colemak,
  Dvorak,
};

// Define the layouts array for comparison
const LAYOUTS = [QWERTY, QWERTZ, Workman, Colemak, Dvorak];

module.exports.LAYOUTS = LAYOUTS;
