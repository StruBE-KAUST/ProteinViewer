AFRAME.registerComponent('startup', {
  /*
    This component stops objects from floating away due to zero gravity.
    Also stops them from moving further than release point when "thrown"
  */

  init: function () {
    // Bind event handlers
    this.physics =    /** @type {AFRAME.System}     */ this.el.sceneEl.systems.physics;
    this.constraint = /** @type {CANNON.Constraint} */ null;

    this.startup = this.startup.bind(this);

    this.el.startup = true;
  },

  play: function () {
    var el = this.el;
    el.addEventListener('startup', this.startup);
  },

  startup: function (evt) {
    this.el.startup = false;
    // called when a controller's trigger is pressed for the first time. Stick all elements to
    // the invisible box at the center and make cartoons follow their hull colliders.
    // Also make boxes follow their respective domains
    var domains = this.el.querySelectorAll('.domain');
    for(var i=0; i<domains.length; i++){
      var domain = domains[i];
      // TODO: emit stick on the hull colliders, and follow on the domain!
      domain.emit('stick');
      domain.emit('follow');
    }
    var boxes = this.el.querySelectorAll('.collision');
    for(var i=0; i<boxes.length; i++){
      var box = boxes[i];
      box.emit('follow');
    }
  }
});


