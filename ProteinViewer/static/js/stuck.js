AFRAME.registerComponent('stuck', {
  /*
    This component sticks the element to the center when released and unsticks it 
    (to make it grabbable) when grabbed
  */

  init: function () {
    // Bind event handlers
    this.physics =    /** @type {AFRAME.System}     */ this.el.sceneEl.systems.physics;
    this.constraint = /** @type {CANNON.Constraint} */ null;

    this.stick = this.stick.bind(this);
    this.onGrab = this.onGrab.bind(this);
  },

  play: function () {
    var el = this.el;
    el.addEventListener('stick', this.stick);
    el.addEventListener('grabbed', this.onGrab);
  },

  onGrab: function (evt) {
    // unstick the domain from the center
    this.physics.world.removeConstraint(this.constraint);
  },

  stick: function() {
    // stick domain to the center
    var el = this.el;
    this.constraint = new CANNON.LockConstraint(el.body, el.sceneEl.querySelector('a-box').body);
    this.physics.world.addConstraint(this.constraint);
  }
});