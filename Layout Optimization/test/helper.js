const mocha = require("mocha");
const coMocha = require("co-mocha");
const { expect } = require("chai");
const fs = require("fs");
const path = require("path");

global.expect = expect;
coMocha(mocha);

// Load both English and German text fixtures
global.TEXT_FIXTURE_EN = `
A long time ago in a galaxy far, far away

It is a period of civil war. Rebel spaceships, striking from a
hidden base, have won their first victory against the evil Galactic Empire.
During the battle, Rebel spies managed to steal secret plans to the
Empire's ultimate weapon, the Death Star, an armored space station
with enough power to destroy an entire planet.
Pursued by the Empire's sinister agents, Princess Leia races home
aboard her starship, custodian of the stolen plans that can save her
people and restore freedom to the galaxy...
`;

global.TEXT_FIXTURE_DE = fs.readFileSync(
  path.join(__dirname, "../text/germanText.txt"),
  "utf8"
);

// Default to English text for backward compatibility
global.TEXT_FIXTURE = global.TEXT_FIXTURE_EN;
