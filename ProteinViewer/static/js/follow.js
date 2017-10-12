AFRAME.registerComponent('follow', {
  /*
    Allows an object without a rigid body to attach to other objects; works like
    a lock constraint.
    This class is used to allow cartoons to "follow" the hulls used as colliders.
    Also used to make the boxes used to indicate domain-linker meeting points to 
    follow their respective domains
  */
  schema: {
    target: {default: ''}
  },

  init: function () {
    this.physics =    /** @type {AFRAME.System}     */ this.el.sceneEl.systems.physics;

    this.follow = this.follow.bind(this);
  },

  play: function () {
    var el = this.el;
    el.addEventListener('follow', this.follow);
  },

  follow: function () {
    var target = document.getElementById(this.data.target);

    console.log(target);

    target.object3D.updateMatrixWorld();
    this.el.object3D.updateMatrixWorld();
    THREE.SceneUtils.attach(this.el.object3D, this.el.sceneEl.object3D, target.object3D);
    
    // if it's a domain-linker meeting point box, add to the domain's boxes

    if(this.el.getAttribute('class') == 'collision'){
      if(!target.boxes){
        target.boxes = [this.el];
      } else {
        boxes = target.boxes;
        boxes.push(this.el);
      }
    }
  }
});