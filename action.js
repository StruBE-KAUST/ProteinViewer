/* global AFRAME */

/**
* Handles events coming from the hand-controls.
* Determines if the entity is grabbed or released.
* Updates its position to move along the controller.
*/

// for the left hand

AFRAME.registerComponent('laction', {

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
    // this.onSwipeStart = this.onSwipeStart.bind(this);
    // this.onSwipeEnd = this.onSwipeEnd.bind(this);

    this.prevRot = {x:0, y:0, z:0};
  },

  play: function () {
    var el = this.el;
    el.addEventListener('hit', this.onHit);
    el.addEventListener('gripclose', this.onGripClose);
    el.addEventListener('gripopen', this.onGripOpen);
    el.addEventListener('pinchclose', this.onPinchClose);
    el.addEventListener('pinchopen', this.onPinchOpen);
    el.addEventListener('swipestart', this.onSwipeStart);
    el.addEventListener('swipeend', this.onSwipeEnd);
  },

  // Don't have pausing functionality yet. Kept commented in case we want to add it later

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
  },

  onPinchOpen: function (evt) {
    var hitEl = this.hitEl;
    this.pinching = false;
    if (!hitEl) { return; }
    hitEl.removeState(this.PINCHED_STATE);
    if(this.grabbing == false) this.hitEl = undefined;
    delete this.newRotation
  },


  onSwipeStart: function (evt) {
    this.swiping = true;
  },

  onSwipeEnd: function (evt) {
    this.swiping = false;
  },

  onHit: function (evt) {
    var hitEl = evt.detail.el;
    // If the element is already grabbed (it could be grabbed by another controller).
    // If the hand is not grabbing the element does not stick.
    // If we're already grabbing something you can't grab again.
    if (!hitEl || hitEl.is(this.GRABBED_STATE) || hitEl.is(this.PINCHED_STATE) || !this.grabbing && !this.pinching || this.hitEl) { return; }
    if(this.grabbing == true) hitEl.addState(this.GRABBED_STATE);
    if(this.pinching == true) hitEl.addState(this.PINCHED_STATE);
    this.hitEl = hitEl;
  },

  tick: function () {
    this.grab();
    this.pinch();
  },

  updateDelta: function () {
    // the position was not changing with the position of the hand, so I defined another
    // attribute to keep track of the position of the leap motion    
    var position = this.el.getAttribute('l-leap');
    var currentPosition = position.pos;
    var previousPosition = this.previousPosition;

    if(!previousPosition){
      previousPosition = currentPosition;
    } else previousPosition = this.previousPosition;

    var cam = this.el.sceneEl.querySelector("a-entity");
    var rot = cam.getAttribute('rotation');

    var rotX = rot.x*0.0174533;
    var rotY = rot.y*0.0174533;

    var delX, delY, delZ;

    this.prevRot = rot;
    delX = (currentPosition.x - previousPosition.x)*Math.cos(rotY) + (currentPosition.z - previousPosition.z)*Math.sin(rotY);
    delY = (currentPosition.y - previousPosition.y)*Math.cos(rotX);
    delZ = (currentPosition.z - previousPosition.z)*Math.cos(rotY) - (currentPosition.x - previousPosition.x)*Math.sin(rotY);

    var deltaPosition = {
      x: delX*0.01,
      y: delY*0.01,
      z: delZ*0.01
    };
    this.previousPosition = currentPosition;
    this.deltaPosition = deltaPosition;
  },

  updateRotation: function () {
    // similar to the position, the rotation had to be manually tracked
    var rotation = this.el.getAttribute('l-leap');
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
});











// As above, but for the right hand

AFRAME.registerComponent('raction', {

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
    // this.onSwipeStart = this.onSwipeStart.bind(this);
    // this.onSwipeEnd = this.onSwipeEnd.bind(this);

    this.prevRot = {x:0, y:0, z:0};
  },

  play: function () {
    var el = this.el;
    el.addEventListener('hit', this.onHit);
    el.addEventListener('gripclose', this.onGripClose);
    el.addEventListener('gripopen', this.onGripOpen);
    el.addEventListener('pinchclose', this.onPinchClose);
    el.addEventListener('pinchopen', this.onPinchOpen);
    el.addEventListener('swipestart', this.onSwipeStart);
    el.addEventListener('swipeend', this.onSwipeEnd);
  },

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
  },

  onPinchOpen: function (evt) {
    var hitEl = this.hitEl;
    this.pinching = false;
    if (!hitEl) { return; }
    hitEl.removeState(this.PINCHED_STATE);
    if(this.grabbing == false) this.hitEl = undefined;
    delete this.newRotation
  },

  onSwipeStart: function (evt) {
    this.swiping = true;
  },

  onSwipeEnd: function (evt) {
    this.swiping = false;
  },

  onHit: function (evt) {
    var hitEl = evt.detail.el;
    // If the element is already grabbed (it could be grabbed by another controller).
    // If the hand is not grabbing the element does not stick.
    // If we're already grabbing something you can't grab again.
    if (!hitEl || hitEl.is(this.GRABBED_STATE) || hitEl.is(this.PINCHED_STATE) || !this.grabbing && !this.pinching || this.hitEl) { return; }
    if(this.grabbing == true) hitEl.addState(this.GRABBED_STATE);
    if(this.pinching == true) hitEl.addState(this.PINCHED_STATE);
    this.hitEl = hitEl;
  },

  tick: function () {
    this.grab();
    this.pinch();
  },

  updateDelta: function () {
    // the position was not changing with the position of the hand, so I defined another
    // attribute to keep track of the position of the leap motion    
    var position = this.el.getAttribute('r-leap');
    var currentPosition = position.pos;
    var previousPosition = this.previousPosition;

    if(!previousPosition){
      previousPosition = currentPosition;
    } else previousPosition = this.previousPosition;

    var cam = this.el.sceneEl.querySelector("a-entity");
    var rot = cam.getAttribute('rotation');

    var rotX = rot.x*0.0174533;
    var rotY = rot.y*0.0174533;

    var delX, delY, delZ;

    this.prevRot = rot;
    delX = (currentPosition.x - previousPosition.x)*Math.cos(rotY) + (currentPosition.z - previousPosition.z)*Math.sin(rotY);
    delY = (currentPosition.y - previousPosition.y)*Math.cos(rotX);
    delZ = (currentPosition.z - previousPosition.z)*Math.cos(rotY) - (currentPosition.x - previousPosition.x)*Math.sin(rotY);

    var deltaPosition = {
      x: delX*0.01,
      y: delY*0.01,
      z: delZ*0.01
    };
    this.previousPosition = currentPosition;
    this.deltaPosition = deltaPosition;
  },

  updateRotation: function () {
    // similar to the position, the rotation had to be manually tracked
    var rotation = this.el.getAttribute('r-leap');
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
        x: rotation.x - a*57.2958,
        y: rotation.y - b*57.2958,
        z: rotation.z - c*57.2958
      });
    }
  }
});