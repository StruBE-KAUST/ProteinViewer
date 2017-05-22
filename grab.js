/* global AFRAME */

/**
* Handles events coming from the hand-controls.
* Determines if the entity is grabbed or released.
* Updates its position to move along the controller.
*/
AFRAME.registerComponent('grab', {

  init: function () {
    this.GRABBED_STATE = 'grabbed';
    this.PINCHED_STATE = 'pinched';
    this.SWIPED_STATE = 'swiped';
    // Bind event handlers
    this.onHit = this.onHit.bind(this);
    this.onGripOpen = this.onGripOpen.bind(this);
    this.onGripClose = this.onGripClose.bind(this);
    // Adding more events:
    // this.onPinchClose = this.onPinchClose.bind(this);
    // this.onPinchOpen = this.onPinchOpen.bind(this);
    // this.onSwipeStart = this.onSwipeStart.bind(this);
    // this.onSwipeEnd = this.onSwipeEnd.bind(this);
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

  pause: function () {
    var el = this.el;
    el.removeEventListener('hit', this.onHit);
    el.removeEventListener('gripclose', this.onGripClose);
    el.removeEventListener('gripopen', this.onGripOpen);
    el.removeEventListener('pinchclose', this.onPinchClose);
    el.removeEventListener('pinchopen', this.onPinchOpen);
    el.removeEventListener('swipestart', this.onSwipeStart);
    el.removeEventListener('swipeend', this.onSwipeEnd);
  },

  onGripClose: function (evt) {
    this.grabbing = true;
    delete this.previousPosition;
    console.log("grabbed");
  },

  onGripOpen: function (evt) {
    var hitEl = this.hitEl;
    this.grabbing = false;
    if (!hitEl) { return; }
    hitEl.removeState(this.GRABBED_STATE);
    this.hitEl = undefined;
    delete this.previousPosition;
  },

  onPinchClose: function (evt) {
    this.pinching = true;
    delete this.previousPosition;
  },

  onPinchOpen: function (evt) {
    var hitEl = this.hitEl;
    this.pinching = false;
    if (!hitEl) { return; }
    hitEl.removeState(this.PINCHED_STATE);
    this.hitEl = undefined;
  },

  onSwipeStart: function (evt) {
    this.swiping = true;
    delete this.previousPosition;
  },

  onSwipeEnd: function (evt) {
    var hitEl = this.hitEl;
    this.swiping = false;
    if (!hitEl) { return; }
    hitEl.removeState(this.SWIPED_STATE);
    this.hitEl = undefined;
  },

  onHit: function (evt) {
    var hitEl = evt.detail.el;
    // If the element is already grabbed (it could be grabbed by another controller).
    // If the hand is not grabbing the element does not stick.
    // If we're already grabbing something you can't grab again.
    if (!hitEl || hitEl.is(this.GRABBED_STATE) || !this.grabbing || this.hitEl) { return; }
    hitEl.addState(this.GRABBED_STATE);
    this.hitEl = hitEl;
  },

  tick: function () {
    var hitEl = this.hitEl;
    var position;
    if (!hitEl) { return; }
    this.updateDelta();
    position = hitEl.getAttribute('position');
    hitEl.setAttribute('position', {
      x: position.x - this.deltaPosition.x,
      y: position.y - this.deltaPosition.z,
      z: position.z - this.deltaPosition.y
    });
  },

  updateDelta: function () {
    // the position was not changing with the position of the hand, so I defined another
    // attribute to keep track of the position of the leap motion    
    var position = this.el.getAttribute('r-leap-position');
    var currentPosition;
    if(!position){
      currentPosition = {x:0, y:0, z:0};
    } else currentPosition = position.pos;
    var previousPosition = this.previousPosition;
    if(!previousPosition){
      previousPosition = currentPosition;
    } else previousPosition = this.previousPosition;
    var deltaPosition = {
      x: (currentPosition.x - previousPosition.x)*0.01,
      y: (currentPosition.y - previousPosition.y)*0.01,
      z: (currentPosition.z - previousPosition.z)*0.01
    };
    this.previousPosition = currentPosition;
    this.deltaPosition = deltaPosition;
  }
});