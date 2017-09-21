AFRAME.registerComponent('event-state', {
  /*
    Makes sure that the controller is loaded before physics systems are attached
  */
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