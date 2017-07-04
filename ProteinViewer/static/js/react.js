AFRAME.registerComponent('react', {
    dependencies: ['raycaster'],

  init: function () {
     this.onHit = this.onHit.bind(this);
     this.onMiss = this.onMiss.bind(this);
     this.el.parentEl.front = false;
     this.el.parentEl.back = false;
  },

  play: function () {
    var el = this.el;
    el.addEventListener('raycaster-intersection', this.onHit);
    el.addEventListener('raycaster-intersection-cleared', this.onMiss);
  },

  onHit: function (evt) {
    var up = this.el.parentEl;
    var el = evt.detail.els[0];
    if(el.className == "model"){
      if(this.el.id == 1 && up.back == false){
        up.back = true;
      } else if(this.el.id == 2 && up.front == false){
        up.front = true;
      }
      if(up.back == true && up.front == true){
        this.el.emit('hit', {el: el});
      }
    }
  },

  onMiss: function (evt) {
    var up = this.el.parentEl;
    var el = evt.detail.el;
    if(el.className == "model"){
      if(this.el.id == 1 && up.back == true){
        up.back = false;
      } else if(this.el.id == 2 && up.front == true){
        up.front = false;
      }
    }
  }
});