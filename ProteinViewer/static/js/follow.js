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
    target.object3D.updateMatrixWorld();
    this.el.object3D.updateMatrixWorld();
    THREE.SceneUtils.attach(this.el.object3D, this.el.sceneEl.object3D, target.object3D);
    if(!target.boxes){
      target.boxes = [this.el];
    } else {
      boxes = target.boxes;
      boxes.push(this.el);
    }
  }
});