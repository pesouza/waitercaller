const SPEED_SCALE = 0.00001;

const game = document.querySelector("#game");
const scoreDisplay = document.querySelector("#score");
const startMessage = document.querySelector("#start-message");
const gameoverMessage = document.querySelector("#gameover-message");

document.addEventListener("keydown", startGame, { once: true });

/* general variables */
let lastTime;
let speedScale;
let score;

/* frame update */
function update(time) { 
  if (lastTime == null) {
    lastTime = time;
    window.requestAnimationFrame(update);
    return;
  }

  const delta = time - lastTime;

  updateGround(delta, speedScale);
  updateWaiter(delta, speedScale);
  updateTable(delta, speedScale);
  updateSpeedScale(delta);
  updateScore(delta);

  if (checkGameOver()) return handleGameOver();

  lastTime = time;
  window.requestAnimationFrame(update);
}

function startGame() {
  lastTime = null;
  speedScale = 1;
  score = 0;
  setupGround();
  setupWaiter();
  setupTable();
  startMessage.classList.add("hide");
  gameoverMessage.classList.add("hide");
  window.requestAnimationFrame(update);
}

/* speeds up the game over time */
function updateSpeedScale(delta) { 
  speedScale += delta * SPEED_SCALE;
}

function updateScore(delta) {
  score += delta * 0.01; 
  scoreDisplay.textContent = Math.floor(score);
}

/* collision conditions */
function checkCollision(rect1, rect2) {
  return (
    rect1.left < rect2.right &&
    rect1.top < rect2.bottom &&
    rect1.right > rect2.left &&
    rect1.bottom > rect2.top
  );
}

function checkGameOver() {
  const waiterRect = getWaiterRect();
  return getTableRects().some(rect => checkCollision(rect, waiterRect)); /* check collision with any of the table */
}

function handleGameOver() {
  setWaiterLose();
  setTimeout(() => {
    document.addEventListener("keydown", startGame, { once: true }); /* prevents accidental click */
    gameoverMessage.classList.remove("hide");
  }, 100);
}




/* HANDLING CSS PROPERTIES */

/* get property value */
function getCustomProperty(elem, prop) {
  return parseFloat(getComputedStyle(elem).getPropertyValue(prop)) || 0;
}

/* set property value */
function setCustomProperty(elem, prop, value) {
  elem.style.setProperty(prop, value);
}

/* increment the property value */
function incrementCustomProperty(elem, prop, inc) {
  setCustomProperty(elem, prop, getCustomProperty(elem, prop) + inc);
}


/* GROUND MOVEMENT */

const GROUND_SPEED = 0.05;
const grounds = document.querySelectorAll(".ground");

function setupGround() {
  setCustomProperty(grounds[0], "--left", 0);
  setCustomProperty(grounds[1], "--left", 300);
}

function updateGround(delta, speedScale) {
  grounds.forEach(ground => {
    incrementCustomProperty(ground, "--left", delta * speedScale * GROUND_SPEED * -1); /* moves the ground according to game speed */

    if (getCustomProperty(ground, "--left") <= -300) {
      incrementCustomProperty(ground, "--left", 600); /* loop the elements */
    }
  });
}

/* WAITERSAUR MOVEMENT */

const waiter = document.querySelector("#waiter");
const JUMP_SPEED = 0.45;
const GRAVITY = 0.0015;
const WAITER_FRAME_COUNT = 6;
const FRAME_TIME = 100;

let isJumping;
let waiterFrame;
let currentFrameTime;
let yVelocity;

function setupWaiter() {
  isJumping = false;
  waiterFrame = 0;
  currentFrameTime = 0;
  yVelocity = 0;

  setCustomProperty(waiter, "--bottom", 0);
  document.removeEventListener("keydown", onJump); /* reset the waitersaur if the player dies while jumping */
  document.addEventListener("keydown", onJump);
}

function updateWaiter(delta, speedScale) {
  handleRun(delta, speedScale);
  handleJump(delta);
}

function getWaiterRect() {
  return waiter.getBoundingClientRect(); /* get the waitersaur hitbox */
}

function setWaiterLose() {
  waiter.src = "../static/site/waiter-lose.png";
}

function handleRun(delta, speedScale) {
  if (isJumping) {
    waiter.src = "../static/site/waiter-jump.png";
    return;
  }

  if (currentFrameTime >= FRAME_TIME) {
    waiterFrame = (waiterFrame + 1) % WAITER_FRAME_COUNT;
    waiter.src = `../static/site/waiter-run-${waiterFrame}.png`; /* switch between images to simulate movement */
    currentFrameTime -= FRAME_TIME;
  }
  currentFrameTime += delta * speedScale;
}

function handleJump(delta) {
  if (!isJumping) return;

  incrementCustomProperty(waiter, "--bottom", yVelocity * delta);

  if (getCustomProperty(waiter, "--bottom") <= 0) {
    setCustomProperty(waiter, "--bottom", 0);
    isJumping = false;
  }

  yVelocity -= GRAVITY * delta;
}

function onJump(e) {
  if (e.code !== "Space" || isJumping) return;

  yVelocity = JUMP_SPEED;
  isJumping = true;
}

/* ADD TABLE */

const TABLE_SPEED = 0.05;
const TABLE_INTERVAL_MIN = 500;
const TABLE_INTERVAL_MAX = 2000;

let nextTableTime;

function setupTable() {
  nextTableTime = TABLE_INTERVAL_MIN;
  document.querySelectorAll(".table").forEach(table => {
    table.remove(); /* remove table when game restart */
  })
}

function updateTable(delta, speedScale) {
  document.querySelectorAll(".table").forEach(table => {
    incrementCustomProperty(table, "--left", delta * speedScale * TABLE_SPEED * -1);
    if (getCustomProperty(table, "--left") <= -100) {
      table.remove(); /* remove table off screen so it doesn't impair game performance */
    }
  })

  if (nextTableTime <= 0) {
    createTable();
    nextTableTime =
      randomizer(TABLE_INTERVAL_MIN, TABLE_INTERVAL_MAX) / speedScale;
  }
  nextTableTime -= delta;
}

function getTableRects() {
  return [...document.querySelectorAll(".table")].map(table => {
    return table.getBoundingClientRect(); /* get the hitbox of all the table on the screen */
  })
}

function createTable() {
  const table = document.createElement("img");
  table.src = "../static/site/table.png";
  table.classList.add("table");
  setCustomProperty(table, "--left", 100);
  game.append(table); 
}

function randomizer(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min); /* choose a number between minimum and maximum */
}
