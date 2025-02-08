 // main.js
 var context;
var wi = 1920;
var hi = 1080;
var prev = performance.now();
var chars = [];
var maxRunningChars = 400;

var fontSize = 20;
var alphaMask = 0.1;
var gridHorizontal;
var gridVertical;

function getRandomHexChar() {
    let possibleChars = "0123456789ABCDEF";
    return possibleChars.charAt(Math.random() * possibleChars.length);
}

function initCanvas(stage) {
    stage.width = wi;
    stage.height = hi;

    gridHorizontal = Math.floor(wi/(fontSize-6));
    gridVertical = Math.floor(hi/(fontSize));

    context.fillStyle="#000000";
    context.fillRect(0, 0, wi, hi);
}

function initChar() {
    var char = {
        x: (Math.floor(Math.random()*gridHorizontal)),
        y: 0,
        tickTime: Math.random()*50+50,
        lastTick: performance.now(),
        char: getRandomHexChar()
    }
    return char;
}

function addBrightness( rgb, brightness ) {
    var multiplier = (100+brightness)/100;
    var result = {};
    result.r = rgb.r * multiplier;
    result.g = rgb.g * multiplier;
    result.b = rgb.b * multiplier;
    return result;
}

function render(time) {
    // Draw a transparent, black rect over everything
    // But not each time
    if ( time - prev > 50 ) {
        context.fillStyle="rgba(0,0,0,"+alphaMask+")";
        context.fillRect(0, 0, wi, hi);
        prev = time;
    }

    // Setup Context Font-Style
    context.font = 'bold 20px Consolas';
    context.textAlign = 'center';
    context.textBaseline = 'middle';

    var iOut = 0;
    for ( var i = 0; i < chars.length; i++ ) {
        var c = chars[i];
        if ( c.y < gridVertical ) { // If Char is still visible
            chars[iOut++] = c; // put it further-up in the array

            // Add a bit more random brightness to the char
            var color = addBrightness({r: 100, g:200, b:100}, Math.random()*70);
            context.fillStyle = "rgb("+color.r+","+color.g+","+color.b+")";
            context.fillText(c.char, c.x*(fontSize-6), c.y*(fontSize));

            // Only move one y-field down if the randomized TickTime is reached
            if ( time - c.lastTick > c.tickTime) {
                c.y++;
                c.lastTick = time;
                // New y-field means new Char, too
                c.char = getRandomHexChar();
            }
        }
    }
    chars.length = iOut; // Adjust array to new length.
    //Every visible char is moved to a point before this, the rest is cut off

    var newChars = 0;
    while (chars.length < maxRunningChars && newChars < 3) {
        chars.push(initChar());
        newChars++;
    }

    requestAnimationFrame(render);
}

function startCanvasDraw() {
    var stage = document.getElementById("mainStage");
    if (stage.getContext) {
        context = stage.getContext("2d");
    }
    else {
        alert("Browser not able to render 2D canvas");
        return;
    }

    initCanvas(stage);

    requestAnimationFrame(render);
}
// import { Pane } from "https://esm.sh/tweakpane@4.0.3";
//
// const state = {
//     fps: 30,
//     color: "#0f0",
//     charset: "01",
//     size: 25
// };
//
// const canvas = document.getElementById("canvas");
// const ctx = canvas.getContext("2d");
//
// let w, h, p;
// const resize = () => {
//     w = canvas.width = window.innerWidth;
//     h = canvas.height = window.innerHeight;
//     p = Array(Math.ceil(w / state.size)).fill(0);
// };
// window.addEventListener("resize", resize);
// resize();
//
// const random = (items) => items[Math.floor(Math.random() * items.length)];
//
// const draw = () => {
//     ctx.fillStyle = "rgba(0,0,0,.05)";
//     ctx.fillRect(0, 0, w, h);
//     ctx.fillStyle = state.color;
//     ctx.font = state.size + "px monospace";
//
//     for (let i = 0; i < p.length; i++) {
//         let v = p[i];
//         ctx.fillText(random(state.charset), i * state.size, v);
//         p[i] = v >= h || v >= 10000 * Math.random() ? 0 : v + state.size;
//     }
// };

let interval = setInterval(draw, 1000 / state.fps);

//
// document.addEventListener("DOMContentLoaded", function() {
//     console.log("JavaScript loaded!");
//
//     // Example: Adding an event listener to a button if available
//     const analyzeButton = document.querySelector("button[type='submit']");
//     if (analyzeButton) {
//         analyzeButton.addEventListener("click", function(event) {
//             alert("Analysis is starting... Please wait.");
//         });
//     }
// });
// document.addEventListener("DOMContentLoaded", function() {
//     console.log("JavaScript loaded!");
//
//     const coin = document.getElementById("coin");
//
//     // Example: Toggle spin animation when the coin is clicked.
//     coin.addEventListener("click", function() {
//         // If the coin has the animation, remove it; otherwise, add it.
//         if (coin.style.animationPlayState === "paused") {
//             coin.style.animationPlayState = "running";
//         } else {
//             coin.style.animationPlayState = "paused";
//         }
//     });
// });
