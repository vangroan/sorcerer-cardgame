import Phaser from "phaser"

import BootScene from "./scenes/BootScene"
import GameScene from "./scenes/GameScene"

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  scale: {
    autoCenter: Phaser.Scale.CENTER_BOTH,
    mode: Phaser.Scale.FIT,
  },
  width: 800,
  height: 600,
  physics: {
    default: "arcade",
    arcade: {
      gravity: { y: 200 },
    },
  },
  callbacks: {
    preBoot: () => {
      document.dispatchEvent(new Event("phaser:preBoot"))
    },
    postBoot: () => {
      document.dispatchEvent(new Event("phaser:preBoot"))
    },
  },
  scene: [BootScene, GameScene],
}

export default config
