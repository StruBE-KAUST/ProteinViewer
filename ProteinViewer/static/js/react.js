AFRAME.registerComponent('react', {
  /*
    This component is needed for the hull colliders. The aframe-physics system 
    does not register a hit event from within a convex hull collider; 
    it only fires events on the surface. This and the associated raycasters 
    can be removed once aframe-physics-system is updated with this feature.
  */
    dependencies: ['raycaster'],

  init: function () {
    // bind the event handlers
     this.onHit = this.onHit.bind(this);
     this.onMiss = this.onMiss.bind(this);
     // using the parent el so that the two raycasters on each controller work
     // together. Only when both front and back are true we register a "hit"
     this.el.parentEl.front = false;
     this.el.parentEl.back = false;
  },

  play: function () {
    var el = this.el;
    el.addEventListener('raycaster-intersection', this.onHit);
    el.addEventListener('raycaster-intersection-cleared', this.onMiss);
  },

  onHit: function (evt) {
    var parent = this.el.parentEl;
    // the raycaster "passes through" elements and hits everything in its path
    // so we take the first element only
    var el = evt.detail.els[0]; 
    if(el.className == "domain"){
      // id 1 points backwards, id 2 points forwards. If a hit event is fired
      // set value on parent element to true to registed the hit.
      if(this.el.id == 1 && parent.back == false){
        parent.back = true;
        parent.backEl = el;
      } else if(this.el.id == 2 && parent.front == false){
        parent.front = true;
        parent.frontEl = el;
      }
      // check if both sides are registering a hit, and if they are hitting the
      // same element. If yes, assume the controller is inside the element and 
      // register a hit
      if(parent.back == true && parent.front == true && parent.backEl == parent.frontEl){
        this.el.emit('hit', {el: el});
      }
    }
  },

  onMiss: function (evt) {
    var parent = this.el.parentEl;
    var el = evt.detail.el;
    if(el.className == "domain"){
      // similar to onHit, but set values on parent element to false to register no hits
      if(this.el.id == 1 && parent.back == true){
        parent.back = false;
        parent.backEl = null;
      } else if(this.el.id == 2 && parent.front == true){
        parent.front = false;
        parent.frontEl = null;
      }
    }
  }
});