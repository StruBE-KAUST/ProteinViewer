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
    // Bind event handlers
    this.onHit = this.onHit.bind(this);
    this.onGripOpen = this.onGripOpen.bind(this);
    this.onGripClose = this.onGripClose.bind(this);
    this.onPinchOpen = this.onPinchOpen.bind(this);
    this.onPinchClose = this.onPinchClose.bind(this);
  },

  play: function () {
    var el = this.el;
    el.addEventListener('hit', this.onHit);
    el.addEventListener('triggerdown', this.onGripClose);
    el.addEventListener('triggerup', this.onGripOpen);
    el.addEventListener('gripdown', this.onPinchClose);
    el.addEventListener('gripup', this.onPinchOpen);
  },

  onGripClose: function (evt) {
    var obj = this.hitEl;
    if(this.hitting == true){
      this.grabbing = true;
      THREE.SceneUtils.attach( obj.object3D, this.el.sceneEl.object3D, this.el.object3D); 
      obj.addState(this.GRABBED_STATE);
    }
  },

  onGripOpen: function (evt) {
    var hitEl = this.hitEl;
    if(this.grabbing == true && hitEl && hitEl.is(this.GRABBED_STATE)){
      var obj = hitEl;
      THREE.SceneUtils.detach( obj.object3D, this.el.object3D, this.el.sceneEl.object3D); 
    }
    this.grabbing = false;
    this.hitEl = undefined;
    this.hitting = false;
    if (!hitEl) { return; }
    hitEl.removeState(this.GRABBED_STATE);
  },

  onPinchClose: function (evt) {
    this.pinching = true;
    var self = this;
    objects = self.el.sceneEl.querySelectorAll('.model');
    objects.forEach(function makeChild(obj){
      if(!obj.is(self.GRABBED_STATE) && !obj.is(self.PINCHED_STATE)){
        THREE.SceneUtils.attach(obj.object3D, self.el.sceneEl.object3D, self.el.object3D); 
        obj.addState(self.PINCHED_STATE);
      }
    })
  },

  onPinchOpen: function (evt) {
    this.pinching = false;
    var self = this;
    objects = self.el.sceneEl.querySelectorAll('.model');
    objects.forEach(function deleteChild(obj){
      if(!obj.is(self.GRABBED_STATE) && obj.is(self.PINCHED_STATE)){
        THREE.SceneUtils.detach(obj.object3D, self.el.object3D, self.el.sceneEl.object3D); 
        obj.removeState(self.PINCHED_STATE);
      }
    })
  },

  onHit: function (evt) {
    var hitEl = evt.detail.el;
    //if (!hitEl || hitEl.is(this.GRABBED_STATE) || this.hitEl) { return; }
    if(!hitEl || this.hitEl == hitEl || hitEl.is(this.GRABBED_STATE) || this.grabbing == true) { return; }
    this.hitting = true;
    this.hitEl = hitEl;
  },

  tick: function () {
    this.grab();
    this.pinch();
  },

  grab: function() { },

  pinch: function() { },
});