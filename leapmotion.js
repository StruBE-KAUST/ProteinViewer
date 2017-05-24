  // Leap motion communication script

  // Store frame for motion functions
  var previousFrame = null;
  var paused = false;

  // Setup Leap loop with frame callback function
  var controllerOptions = {};

  var lgrabbing, lpinching, lswiping, rgrabbing, rpinching, rswiping = false;
  var newrgrab, newrpinch, newrswipe, newlgrab, newlpinch, newlswipe = true;
  var rPos, lPos, rRot, lRot = {x:0, y:0, z:0}

  // to use HMD mode, set to true:
  controllerOptions.optimizeHMD = false;

  Leap.loop(controllerOptions, function(frame) {
    if (paused) {
      return; // Skip this update
    }

    if (frame.hands.length > 0) {
      for (var i = 0; i < frame.hands.length; i++) {
        var hand = frame.hands[i];
        var handPos = hand.palmPosition;

        // if the hand is a left hand: 
        if(hand.type == 'left'){
          lPos = { x: handPos[0], y: handPos[1], z: handPos[2] };

          if(!previousFrame){}
            else {
              var a = hand.rotationAngle(previousFrame, [1, 0, 0]);
              var b = hand.rotationAngle(previousFrame, [0, 1, 0]);
              var c = hand.rotationAngle(previousFrame, [0, 0, 1]);
              lRot = { x: a, y: b, z: c };
            }

          if(hand.grabStrength > 0.50 && newlgrab == true) {
            lgrabbing = true;
          } else if(hand.grabStrength < 0.50) {
            lgrabbing = false;
          }

          if(hand.pinchStrength > 0.50 && newlpinch == true) {
            lpinching = true;
          } else if(hand.pinchStrength < 0.50) {
            lpinching = false;
          }

          var vel = hand.palmVelocity;
          var speed = Math.sqrt(Math.pow(vel[0],2) + Math.pow(vel[1],2) + Math.pow(vel[2],2));

          if(speed > 1200){
            lswiping = true;
            speed = 0;
          } else lswiping = false;
        } 

        // same as above, but for the right hand
        else if(hand.type == 'right') {

          rPos = { x: handPos[0], y: handPos[1], z: handPos[2] };

          if(!previousFrame){}
            else {
              var a = hand.rotationAngle(previousFrame, [1, 0, 0]);
              var b = hand.rotationAngle(previousFrame, [0, 1, 0]);
              var c = hand.rotationAngle(previousFrame, [0, 0, 1]);
              rRot = { x: a, y: b, z: c };
            }

          if(hand.grabStrength > 0.50 && newrgrab == true) {
            rgrabbing = true;
          } else if(hand.grabStrength < 0.50){
            rgrabbing = false;
          }

          if(hand.pinchStrength > 0.50 && newrpinch == true) {
            rpinching = true;
          } else if(hand.pinchStrength < 0.50) {
            rpinching = false;
          }

          var vel = hand.palmVelocity;
          var speed = Math.sqrt(Math.pow(vel[0],2) + Math.pow(vel[1],2) + Math.pow(vel[2],2));

          if(speed > 1200){
            rswiping = true;
            speed = 0;
          } else rswiping = false;
        }
      }
    } else {
      rswiping, rgrabbing, rpinching, lswiping, lgrabbing, lpinching = false;
    }

  // Store frame for motion functions
    previousFrame = frame;
  })


  AFRAME.registerComponent('l-events', {
    tick: (function(){
      if(lgrabbing == true && newlgrab == true){
        newlgrab = false;
        this.el.emit('gripclose', {});
      } else if (lgrabbing == false) {
        newlgrab = true;
        this.el.emit('gripopen', {});
      }

      if(lpinching == true && newlpinch == true){
        newlpinch = false;
        this.el.emit('pinchclose', {});
      } else if (lpinching == false) {
        newlpinch = true;
        this.el.emit('pinchopen', {});
      }

      if(lswiping == true && newlswipe == true){
        newlswipe = false;
        this.el.emit('swipestart', {});
      } else if (lswiping == false) {
        newlswipe = true;
        this.el.emit('swipeend', {});
      }
    })
  })

  AFRAME.registerComponent('r-events', {
    tick: (function(){
      if(rgrabbing == true && newrgrab == true){
        newrgrab = false;
        this.el.emit('gripclose', {});
      } else if (rgrabbing == false) {
        newrgrab = true;
        this.el.emit('gripopen', {});
      }

      if(rpinching == true && newrpinch == true){
        newrpinch = false;
        this.el.emit('pinchclose', {});
      } else if (rpinching == false) {
        newrpinch = true;
        this.el.emit('pinchopen', {});
      }

      if(rswiping == true && newrswipe == true){
        newrswipe = false;
        this.el.emit('swipestart', {});
      } else if (rswiping == false) {
        newrswipe = true;
        this.el.emit('swipeend', {});
      }
    })
  })

  AFRAME.registerComponent('r-leap', {
    schema: {
      pos: {
        type: 'vec3',
        default: rPos
      },
      rot: {
        type: 'vec3',
        default: rRot
      }
    },
    tick: function(){
      this.data.pos = rPos;
      this.data.rot = rRot;
    }
  })

  AFRAME.registerComponent('l-leap', {
    schema: {
      pos: {
        type: 'vec3',
        default: lPos
      },
      rot: {
        type: 'vec3',
        default: lRot
      }
    },
    tick: function(){
      this.data.pos = lPos;
      this.data.rot = lRot;
    }
  })