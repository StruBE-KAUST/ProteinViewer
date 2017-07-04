AFRAME.registerComponent('objects-collide', {

  init: function () {
    this.onHit = this.onHit.bind(this);
    this.collided = false;
  },

  play: function () {
    var el = this.el;
    el.addEventListener('hit', this.onHit);
  },

  onHit: function (evt) {
    var hitEl = evt.detail.el;
    if(!hitEl) { this.hitting = false; return; }
    if(this.hitting == true) this.pos = this.el.parentEl.getAttribute('position');
    else this.hitting = true;
  },

  tick: function () {
    if(this.hitting == true){
      this.el.parentEl.setAttribute('position', this.pos);
    } else this.hitting = false;
  }
});