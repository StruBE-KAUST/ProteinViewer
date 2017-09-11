AFRAME.registerComponent('event-state', {
  schema: { 
    event: { default: 'model-loaded' }, 
    state: { default: 'loaded' }
  },
  init: function () {
    this.setStateB = this.setState.bind(this);
  },
  play: function() {
    this.el.addEventListener(this.data.event, this.setStateB);
  },
  setState: function (evt) {
    this.el.addState(this.data.state);
  }
});