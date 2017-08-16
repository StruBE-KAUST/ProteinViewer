AFRAME.registerComponent('action', {
/**
 * Handles events coming from the hand-controls.
 * Determines if the entity is grabbed or released.
 * Updates its position to move along the controller.
 */
  init: function () {
    // initializes physics system and binds event handlers
    this.GRABBED_STATE = 'grabbed';

    this.grabbing = false;
    this.hitEl =      /** @type {AFRAME.Element}    */ null;
    this.physics =    /** @type {AFRAME.System}     */ this.el.sceneEl.systems.physics;
    this.constraint = /** @type {CANNON.Constraint} */ null;

    // Bind event handlers
    this.onHit = this.onHit.bind(this);
    this.onGripOpen = this.onGripOpen.bind(this);
    this.onGripClose = this.onGripClose.bind(this);
    scene = this.el.sceneEl;
    scene.grabbingControllers = 0;
    scene.grabNum = 0;
  },

  play: function () {
    var el = this.el;
    el.addEventListener('hit', this.onHit);
    el.addEventListener('triggerdown', this.onGripClose);
    el.addEventListener('triggerup', this.onGripOpen);
  },

  pause: function () {
    var el = this.el;
    el.removeEventListener('hit', this.onHit);
    el.removeEventListener('triggerdown', this.onGripClose);
    el.removeEventListener('triggerup', this.onGripOpen);
  },

  onGripClose: function (evt) {
    this.grabbing = true;
  },

  onGripOpen: function (evt) {
    var hitEl = this.hitEl;
    this.grabbing = false;  
    if (!hitEl) { return; }
    // if there is an entity, release it by removing the lock constraint that holds
    // it to the controller. Then call sendNewCoords() to update the linker
    hitEl.removeState(this.GRABBED_STATE);
    hitEl.emit('released');
    this.hitEl = undefined;
    this.physics.world.removeConstraint(this.constraint);
    this.constraint = null;
    scene = this.el.sceneEl;
    scene.grabbingControllers--;
    if(scene.grabbingControllers == 0){
      sendNewCoords(scene.grabNum);
      scene.grabNum++;
    }
  },

  onHit: function (evt) {
    var hitEl = evt.detail.el;
    // Grab conditions:
    // If the element is already grabbed (it could be grabbed by another controller), can't grab it.
    // If the hand is not grabbing, the element does not stick.
    // If we're already grabbing something you can't grab again.
    if (!hitEl || hitEl.is(this.GRABBED_STATE) || !this.grabbing || this.hitEl) { return; }
    hitEl.addState(this.GRABBED_STATE);
    this.hitEl = hitEl;
    // attach the entity to the grabbing controller
    this.constraint = new CANNON.LockConstraint(this.el.body, hitEl.body);
    this.physics.world.addConstraint(this.constraint);
    hitEl.emit('grabbed');
    scene = this.el.sceneEl;
    scene.grabbingControllers++;
  }
});