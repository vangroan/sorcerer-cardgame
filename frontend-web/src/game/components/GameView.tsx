import React, { useEffect } from "react"
import Phaser from "phaser"

import config from "../config"

function GameView() {
  // Boot Phaser.js
  useEffect(() => {
    console.debug("Creating game...")
    const game = new Phaser.Game(config)

    // Cleanup callback
    return () => {
      console.debug("Destroying game...")
      game.destroy(true)
    }
  }, [])

  return <div id="phaser-game" className="GameView" />
}

// Attempt to minimise re-rendering, otherwise
// our Phaser.js game state gets flushed.
export default React.memo(GameView)
