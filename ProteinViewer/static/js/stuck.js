AFRAME.registerComponent('stuck', {

  init: function () {
    // Bind event handlers
    this.physics =    /** @type {AFRAME.System}     */ this.el.sceneEl.systems.physics;
    this.constraint = /** @type {CANNON.Constraint} */ null;

    this.go = this.go.bind(this);
    this.onGrab = this.onGrab.bind(this);
    this.onRelease = this.onRelease.bind(this);

    this.el.sceneEl.startup = true;
  },

  play: function () {
    var el = this.el;
    el.addEventListener('stick', this.go);
    el.addEventListener('grabbed', this.onGrab);
    el.addEventListener('released', this.onRelease);
  },

  onGrab: function (evt) {
    if(this.el.sceneEl.startup == true){
      var els = this.el.sceneEl.querySelectorAll('.domain');
      var self = this;
      this.el.sceneEl.startup = false;
      if(els.length == 0){ return; }
      for(var i=0; i<els.length; i++){
        var el = els[i];
        if(el == self.el){
          el.emit('follow');
          continue;
        } else {
          el.emit('stick');
          el.emit('follow');
        }
      }
    } else this.physics.world.removeConstraint(this.constraint);
  },

  onRelease: function (evt) {
    var el = this.el;
    this.constraint = new CANNON.LockConstraint(el.body, el.sceneEl.querySelector('a-box').body);
    this.physics.world.addConstraint(this.constraint);
  },

  go: function() {
    var el = this.el;
    this.constraint = new CANNON.LockConstraint(el.body, el.sceneEl.querySelector('a-box').body);
    this.physics.world.addConstraint(this.constraint);
  }
});