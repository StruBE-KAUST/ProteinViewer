AFRAME.registerComponent('follow', {
  schema: {
    target: {default: ''}
  },

  init: function () {
    this.physics =    /** @type {AFRAME.System}     */ this.el.sceneEl.systems.physics;

    this.onDone = this.onDone.bind(this);
  },

  play: function () {
    var el = this.el;
    el.addEventListener('follow', this.onDone);
  },

  onDone: function () {
    var target = document.getElementById(this.data.target);
    THREE.SceneUtils.attach(target.object3D, this.el.sceneEl.object3D, this.el.object3D); 
  }
});