/* global AFRAME */

/**
* Handles events coming from the hand-controls.
* Determines if the entity is grabbed or released.
* Updates its position to move along the controller.
*/

AFRAME.registerComponent('action', {

  init: function () {
    this.GRABBED_STATE = 'grabbed';
    this.PINCHED_STATE = 'pinched';
    this.SWIPED_STATE = 'swiped';
    // Bind event handlers
    this.onHit = this.onHit.bind(this);
    this.onGripOpen = this.onGripOpen.bind(this);
    this.onGripClose = this.onGripClose.bind(this);
    // Adding more events:
    this.onPinchClose = this.onPinchClose.bind(this);
    this.onPinchOpen = this.onPinchOpen.bind(this);

    this.prevRot = {x:0, y:0, z:0};
  },

  play: function () {
    var el = this.el;
    el.addEventListener('hit', this.onHit);
    el.addEventListener('gripclose', this.onGripClose);
    el.addEventListener('gripopen', this.onGripOpen);
    el.addEventListener('pinchclose', this.onPinchClose);
    el.addEventListener('pinchopen', this.onPinchOpen);
  },

  onGripClose: function (evt) {
    this.grabbing = true;
    delete this.previousPosition;
  },

  onGripOpen: function (evt) {
    var hitEl = this.hitEl;
    this.grabbing = false;
    if (!hitEl) { return; }
    hitEl.removeState(this.GRABBED_STATE);
    if(this.pinching == false) this.hitEl = undefined;
    delete this.previousPosition;
  },

  onPinchClose: function (evt) {
    this.pinching = true;
    delete this.newRotation;
    delete this.previousPosition;
  },

  onPinchOpen: function (evt) {
    var hitEl = this.hitEl;
    this.pinching = false;
    if (!hitEl) { return; }
    hitEl.removeState(this.PINCHED_STATE);
    if(this.grabbing == false) this.hitEl = undefined;
    delete this.newRotation;
    delete this.previousPosition;
  },

  onHit: function (evt) {
    var hitEl = evt.detail.el;

    var hand = this.el.getAttribute('leap-hand').hand;
    var str;
    if(hand == "left"){
      if(this.grabbing == true) {
        if (!hitEl || hitEl.is(this.GRABBED_STATE) || hitEl.is(this.PINCHED_STATE) || !this.grabbing && !this.pinching || this.hitEl) { return; }
        hitEl.addState(this.GRABBED_STATE);
        this.hitEl = hitEl;
      } else if(this.pinching == true) {
        if (!this.grabbing && !this.pinching) { return; }
        if (!hitEl){}
          else if ( hitEl.is(this.GRABBED_STATE) || hitEl.is(this.PINCHED_STATE)) { return; }
      }
    } else {
      if (!hitEl || hitEl.is(this.GRABBED_STATE) || hitEl.is(this.PINCHED_STATE) || !this.grabbing && !this.pinching || this.hitEl) { return; }
      if(this.grabbing == true) hitEl.addState(this.GRABBED_STATE);
      if(this.pinching == true) hitEl.addState(this.PINCHED_STATE);
      this.hitEl = hitEl;
    }
  },

  tick: function () {
    this.grab();
    this.pinch();
  },

  updateDelta: function () {
    // the position was not changing with the position of the hand, so I defined another
    // attribute to keep track of the position of the leap motion    
    var hand = this.el.getAttribute('leap-hand').hand;
    var str;
    if(hand == "left"){
      str = 'l-leap';
    } else str = 'r-leap';

    var position = this.el.getAttribute(str);
    var currentPosition = position.pos;
    var previousPosition = this.previousPosition;

    if(!previousPosition){
      previousPosition = currentPosition;
    } else previousPosition = this.previousPosition;

    var cam = this.el.sceneEl.querySelector("a-entity");
    var rot = cam.getAttribute('rotation');

    var rotX = rot.x*0.0174533;
    var rotY = rot.y*0.0174533;
    var rotZ = rot.z*0.0174533;

    var delX, delY, delZ;

    this.prevRot = rot;

    var leapVR = controllerOptions.optimizeHMD;
    var sceneVR = this.el.sceneEl.getAttribute('leap').vr;

    if(leapVR == true && sceneVR == true){
      delX = (previousPosition.x - currentPosition.x)*Math.cos(rotZ)*Math.cos(rotY) - (previousPosition.z - currentPosition.z)*Math.sin(rotZ) + (previousPosition.y - currentPosition.y)*Math.sin(rotY); 
      delY = (previousPosition.z - currentPosition.z)*Math.cos(rotZ)*Math.cos(rotX) + (previousPosition.x - currentPosition.x)*Math.sin(rotZ) - (previousPosition.y - currentPosition.y)*Math.sin(rotX); 
      delZ = (previousPosition.y - currentPosition.y)*Math.cos(rotY)*Math.cos(rotX) - (previousPosition.x - currentPosition.x)*Math.sin(rotY) + (previousPosition.z - currentPosition.z)*Math.sin(rotX); 
    } else {
      delX = (currentPosition.x - previousPosition.x)*Math.cos(rotY) + (currentPosition.z - previousPosition.z)*Math.sin(rotY);
      delY = (currentPosition.y - previousPosition.y)*Math.cos(rotX);
      delZ = (currentPosition.z - previousPosition.z)*Math.cos(rotY) - (currentPosition.x - previousPosition.x)*Math.sin(rotY);
    }

    var deltaPosition = { x: delX*0.01, y: delY*0.01, z: delZ*0.01 };
    this.previousPosition = currentPosition;
    this.deltaPosition = deltaPosition;
  },

  updateRotation: function () {
    // similar to the position, the rotation had to be manually tracked
    var hand = this.el.getAttribute('leap-hand').hand;
    var str;
    if(hand == "left"){
      str = 'l-leap';
    } else str = 'r-leap';

    var rotation = this.el.getAttribute(str);
    var currentRotation;
    if(!rotation){
      currentRotation = {x:0, y:0, z:0};
    } else currentRotation = rotation.rot;
    this.newRotation = currentRotation;
  },

  grab: function() {
    var hitEl = this.hitEl;
    if(this.grabbing == true){
      var position;
      if (!hitEl) { return; }
      this.updateDelta();
      position = hitEl.getAttribute('position');
      hitEl.setAttribute('position', {
        x: position.x + this.deltaPosition.x,
        y: position.y + this.deltaPosition.y,
        z: position.z + this.deltaPosition.z
      });
    }
  },

  pinch: function() {
    var hand = this.el.getAttribute('leap-hand').hand;
    if(hand == "left"){
      if(this.pinching == true && this.grabbing == false){
        this.updateDelta();
        var mols =  this.el.sceneEl.querySelectorAll('.model');
        var self = this;

        mols.forEach(function move (el) {
          position = el.getAttribute('position');
          el.setAttribute('position', {
            x: position.x + self.deltaPosition.x,
            y: position.y + self.deltaPosition.y,
            z: position.z + self.deltaPosition.z
          });
        });
      }
    } else {
      var hitEl = this.hitEl;
      if(this.pinching == true && this.grabbing == false){
        var rotation;
        if (!hitEl) { return; }
        this.updateRotation();
        rotation = hitEl.getAttribute('rotation');
        var a = this.newRotation.x;
        var b = this.newRotation.y;
        var c = this.newRotation.z;
        hitEl.setAttribute('rotation', {
          x: rotation.x - a*57.2958*0.5,
          y: rotation.y - b*57.2958*0.5,
          z: rotation.z - c*57.2958*0.5
        });
      }
    }
  },
});


  // Don't have pausing functionality yet. Kept commented in case we want to add it later
  // simple insert above, below the play function

  // pause: function () {
  //   var el = this.el;
  //   el.removeEventListener('hit', this.onHit);
  //   el.removeEventListener('gripclose', this.onGripClose);
  //   el.removeEventListener('gripopen', this.onGripOpen);
  //   el.removeEventListener('pinchclose', this.onPinchClose);
  //   el.removeEventListener('pinchopen', this.onPinchOpen);
  //   el.removeEventListener('swipestart', this.onSwipeStart);
  //   el.removeEventListener('swipeend', this.onSwipeEnd);
  // },