// import React, { useEffect } from "react"
// import { useDispatch, useSelector } from "react-redux"
// import Phaser from "phaser"
// import { WebSocketSubject } from "rxjs/webSocket"

// import reactLogo from "../assets/react.svg"

// import { selectJoinKey } from "./selectors"

// class GameScene extends Phaser.Scene {
//   joinKey?: string
//   joinKeyText?: Phaser.GameObjects.Text

//   constructor() {
//     super("Game")
//     console.debug("GameScene constructed")
//   }

//   init(data: any) {
//     data.connectSubject.subscribe({
//       next: (subject) => {
//         console.debug("GameScene: ", subject)
//       }
//     })
//   }

//   preload() {
//     this.load.image('logo', reactLogo);
//     console.debug("GameScene preloaded")
//   }

//   create() {
//     console.debug("GameScene create")
//     const logo = this.add.image(400, 70, 'logo')
//     this.joinKeyText = this.add.text(0, 0, "Join key:")

//     this.tweens.add({
//       targets: logo,
//       y: 350,
//       duration: 1500,
//       ease: 'Sine.inOut',
//       yoyo: true,
//       repeat: -1
//     })

//     const card1 = this.add.container(100, 100)

//     const rect1 = this.add.rectangle(0, 0, 100, 140, 0x6666ff)

//     const text1 = this.add.text(-50, -70, 'Dark Elf');

//     card1.add(rect1)
//     card1.add(text1)

//     this.tweens.add({
//       targets: card1,
//       scaleX: 0.25,
//       scaleY: 0.5,
//       yoyo: true,
//       repeat: -1,
//       ease: 'Sine.easeInOut'
//     })
//   }

//   setJoinKey(joinKey: string) {
//     this.joinKey = joinKey
//     if (joinKey && this.joinKeyText) {
//       this.joinKeyText.setText(`Join key: ${joinKey}`)
//     }
//   }
// }

// export interface GameProps {
//   getSubject: () => WebSocketSubject<unknown> | undefined,
// }

// function Game(props: { getSubject: any, connectSubject: any }) {
//   console.debug("Game re-rendered")

//   const dispatch = useDispatch()
//   dispatch({type: "WS_CONNECT"})

//   useEffect(() => {
//     // const subscription = props.connectSubject.subscribe({
//     //   next: (subject) => {
//     //     console.debug("Game component: ", subject)
//     //   }
//     // })

//     const bootScene = {
//       preload: () => {},
//       create: () => {
//         console.debug("Boot create")
//         const self = this
//         self.subscription = props.connectSubject.subscribe({
//           next: (subject) => {
//             console.debug("Boot create: ", subject)
//             self.scene.start("Game", { connectSubject: props.connectSubject })
//             self.subscription.unsubscribe()
//           }
//         })
//       }
//     }

//     const config: Phaser.Types.Core.GameConfig = {
//       type: Phaser.AUTO,
//       width: 800,
//       height: 600,
//       physics: {
//         default: 'arcade',
//         arcade: {
//           gravity: { y: 200 }
//         }
//       },
//       scene: [bootScene],
//     }

//     const game = new Phaser.Game(config)

//     return () => {
//       console.debug("Game destroy")
//       subscription.unsubscribe()
//       game.destroy(true)
//     }
//   }, [props.connectSubject])

//   return (
//     <div id="phaser-game" />
//   )
// }

// // Attempt to minimise re-rendering, otherwise
// // our Phaser.js game state gets flushed.
// export default React.memo(Game)
