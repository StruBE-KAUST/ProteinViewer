  // Leap motion communication script

  // Store frame for motion functions
  var previousFrame = null;
  var paused = false;

  // Setup Leap loop with frame callback function
  var controllerOptions = {
    // enableGestures: true // find a way to make use of gestures!
  };

  var lgrabbing = false;
  var lpinching = false;
  var lswiping = false;

  var rgrabbing = false;
  var rpinching = false;
  var rswiping = false;

  var newgrab = true;

  // to use HMD mode:
  controllerOptions.optimizeHMD = true;

  var rPos = {x:0, y:0, z:0}
  var lPos = {x:0, y:0, z:0}

  Leap.loop(controllerOptions, function(frame) {
    if (paused) {
      return; // Skip this update
    }

    if (frame.hands.length > 0) {
      for (var i = 0; i < frame.hands.length; i++) {
        var hand = frame.hands[i];
        var handPos = hand.palmPosition;


        if(hand.type == 'left'){

          lPos = {
            x: handPos[0],
            y: handPos[1],
            z: handPos[2]
          }

          if(hand.grabStrength > 0.50) {
            lgrabbing = true;
          } else lgrabbing = false;

          if(hand.pinchStrength > 0.50) {
            lpinching = true;
          } else lpinching = false;

          var vel = hand.palmVelocity;
          var speed = Math.sqrt(Math.pow(vel[0],2) + Math.pow(vel[1],2) + Math.pow(vel[2],2));

          if(speed > 1200){
            lswiping = true;
            speed = 0;
          } else lswiping = false;
        } else if(hand.type == 'right') {

          rPos = {
            x: handPos[0],
            y: handPos[1],
            z: handPos[2]
          }

          if(hand.grabStrength > 0.50 && newgrab == true) {
            rgrabbing = true;
          } else if(hand.grabStrength < 0.50){
            rgrabbing = false;
          }

          if(hand.pinchStrength > 0.80) {
            rpinching = true;
          } else rpinching = false;

          var vel = hand.palmVelocity;
          var speed = Math.sqrt(Math.pow(vel[0],2) + Math.pow(vel[1],2) + Math.pow(vel[2],2));

          if(speed > 1200){
            rswiping = true;
            speed = 0;
          } else rswiping = false;
        }
      }
    } else {
      rswiping = false;
      rgrabbing = false;
      rpinching = false;
      lswiping = false;
      lgrabbing = false;
      lpinching = false;
    }

  // Store frame for motion functions
    previousFrame = frame;
  })


  AFRAME.registerComponent('l-events', {
    tick: (function(){
      if(lgrabbing == true){
        this.el.emit('gripclose', {});
      } else {
        this.el.emit('gripopen', {});
      }

      // if(lpinching == true){
      //   this.el.emit('pinchclose', {el: this});
      // } else {
      //   this.el.emit('pinchopen', {el: this});
      // }

      // if(lswiping == true){
      //   this.el.emit('swipestart', {el: this});
      // } else {
      //   this.el.emit('swipeend', {el: this});
      // }
    })
  })

  AFRAME.registerComponent('r-events', {
    tick: (function(){
      if(rgrabbing == true && newgrab == true){
        newgrab = false;
        this.el.emit('gripclose', {});
      } else if (rgrabbing == false) {
        newgrab = true;
        this.el.emit('gripopen', {});
      }

      // if(rpinching == true){
      //   this.el.emit('pinchclose', {el: this});
      // } else {
      //   this.el.emit('pinchopen', {el: this});
      // }

      // if(rswiping == true){
      //   this.el.emit('swipestart', {el: this});
      // } else {
      //   this.el.emit('swipeend', {el: this});
      // }
    })
  })

  AFRAME.registerComponent('r-leap-position', {
    schema: {
      pos: {
        type: 'vec3',
        default: rPos
      }
    },
    tick: function(){
      this.data.pos = rPos;
    }
  })

  // AFRAME.registerComponent('r-leap-rotation', {
  //   tick: (function(){
  //     return rRot;
  //   })
  // })

  AFRAME.registerComponent('l-leap-position', {
    schema: {
      default: lPos
    },
  })

  // AFRAME.registerComponent('l-leap-rotation', {
  //   tick: (function(){
  //     return lRot;
  //   })
  // })