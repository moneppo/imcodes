ctx.fillStyle = "#00A308";
ctx.beginPath();
ctx.arc(220, 220, 50, 0, Math.PI*2, true);
ctx.closePath();
ctx.fill();

ctx.fillStyle = "#FF1C0A";
ctx.beginPath();
ctx.arc(100, 100, 100, 0, Math.PI*2, true);
ctx.closePath();
ctx.fill();

//the rectangle is half transparent
ctx.fillStyle = "rgba(255, 255, 0, .5)"
ctx.beginPath();
ctx.rect(15, 150, 120, 120);
ctx.closePath();
ctx.fill();

console.log("Yay!");