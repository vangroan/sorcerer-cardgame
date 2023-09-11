import Phaser from "phaser"

class GameScene extends Phaser.Scene {
  constructor() {
    super("game")
  }

  preload() {}

  create() {
    this.add.text(0, 0, "Hello, world!")
  }
}

export default GameScene
