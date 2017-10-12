function vanishLinkers(controller){
  /*
  Makes linkers directly affected by this move vanish
  @param controller: the controller making the move
  @type controller: TODO: Enter type
  @param hitEl: the element hit by the controller
  @type hitEl: TODO: Enter type
  */
  boxes = controller.hitEl.boxes;
  lines = [];
  links = [];
  for(var i=0; i<boxes.length; i++){
    line = boxes[i].getAttribute('line');
    lines.push(line);
    link = boxes[i].getAttribute('link');
    links.push(link);
  }
  controller.lines = lines;

  console.log(lines);
  console.log(links);

  for(var i=0; i<links.length; i++){
    linker = document.getElementById('link' + links[i]);
    linker.setAttribute('obj-model', 'obj', '../../media/empty.obj');
    linker.setAttribute('obj-model', 'mtl', '../../media/empty.mtl');
  }
}


AFRAME.registerComponent('action', {
/**
 * Handles events coming from the hand-controls.
 * Determines if the entity is grabbed or released.
 * Updates its position to move along the controller.
 */
  init: function () {
    // initializes physics system and binds event handlers
    this.GRABBED_STATE = 'grabbed';

    this.grabbing = false;
    this.gripping = false;
    this.holding = false;
    this.hitEl =      /** @type {AFRAME.Element}    */ null;
    this.physics =    /** @type {AFRAME.System}     */ this.el.sceneEl.systems.physics;
    this.constraint = /** @type {CANNON.Constraint} */ null;

    // Bind event handlers
    this.onHit = this.onHit.bind(this);
    this.onTriggerUp = this.onTriggerUp.bind(this);
    this.onTriggerDown = this.onTriggerDown.bind(this);
    // TODO: use grip to move entire molecule as one
    // this.onGripUp = this.onGripUp.bind(this);
    // this.onGripDown = this.onGripDown.bind(this);
    scene = this.el.sceneEl;
    scene.grabbingControllers = 0;
    scene.loading = false;
  },

  // TODO: Make event listeners listen for mouse inputs too!

  play: function () {
    var el = this.el;
    el.addEventListener('hit', this.onHit);
    el.addEventListener('triggerdown', this.onTriggerDown);
    el.addEventListener('triggerup', this.onTriggerUp);

    // el.addEventListener('gripdown', this.onGripDown);
    // el.addEventListener('gripup', this.onGripUp);
  },

  onTriggerDown: function (evt) {
    scene = this.el.sceneEl;
    if(scene.startup == true){
      scene.emit('startup');
    }

    if(!this.holdEl && this.hitEl && !this.hitEl.is(this.GRABBED_STATE)){
      // TODO: need to test the last statement in the if; see what happens if we try 
      // grab an already grabbed domain. Do we count presses?
      this.grabbing = true;
      scene.presses = scene.presses + 1;
    }
  },

  onTriggerUp: function (evt) {
    var hitEl = this.holdEl;
    this.grabbing = false; 
    this.holding = false;
    if (!hitEl) { return; }
    // if there is an entity, release it by removing the lock constraint that holds
    // it to the controller
    this.physics.world.removeConstraint(this.constraint);
    this.constraint = null;
    hitEl.removeState(this.GRABBED_STATE);
    hitEl.emit('stick');
    this.hitEl = undefined;
    scene = this.el.sceneEl;
    scene.grabbingControllers--;
    if(scene.grabbingControllers == 0){
      // if no controllers are grabbing, call sendNewCoordinates to create linkers and all for
      // the current domain configuration
      scene.version++;
      sendNewCoordinates(scene.version);
    }
    this.holdEl = null;
  },


  // TODO: Create functions for the "grip" buttons so that we can move all the 
  // domains/linkers/etc at once so that it moves like a single "molecule"

  // onGripDown: function (evt) {
  //   scene = this.el.sceneEl;
  //   // grip or trigger, whichever is used first will trigger the boxes to stick 
  //   // to their respective domains
  //   if(scene.first == 0){
  //     scene.first = 1;
  //     boxes = document.querySelectorAll('.collision');
  //     console.log(boxes);
  //     for(var i=0; i<boxes.length; i++){
  //       boxes[i].emit('follow');
  //     }
  //   }

  //   if(scene.loading == false && this.grabbing == false){
  //     this.gripping = true;
  //     doms = document.querySelectorAll('.domain');
  //     links = document.querySelectorAll('.linker');
  //     for(i=0; i<doms.length; i++){
  //       doms[i].emit('grabbed');
  //     }
  //     for(i=0; i<links.length; i++){
  //       links[i].object3D.updateMatrixWorld();
  //       this.el.object3D.updateMatrixWorld();
  //       THREE.SceneUtils.attach(links[i].object3D, this.el.sceneEl.object3D, this.el.object3D);
  //     }
  //   }
  // },

  // onGripUp: function (evt) {
  //   if(this.gripping == true){
  //     doms = document.querySelectorAll('.domain');
  //     links = document.querySelectorAll('.linker');
  //     for(i=0; i<doms.length; i++){
  //       doms[i].emit('stick');
  //     }
  //     for(i=0; i<links.length; i++){
  //       THREE.SceneUtils.detach(links[i].object3D, this.el.object3D, this.el.sceneEl.object3D);
  //     }
  //     this.gripping = false;
  //   }
  // },


  onHit: function (evt) {
    var hitEl = evt.detail.el;
    this.hitEl = hitEl;
    // Grab conditions:
    // If the element is already grabbed (it could be grabbed by another controller), can't grab it.
    // If the hand is not grabbing, the element does not stick.
    // If we're already grabbing something you can't grab again.
    if (!hitEl || hitEl.is(this.GRABBED_STATE) || !this.grabbing || this.holdEl) { return; }
    hitEl.addState(this.GRABBED_STATE);
    this.holding = true;
    this.holdEl = hitEl;
    // attach the entity to the grabbing controller
    this.constraint = new CANNON.LockConstraint(this.el.body, hitEl.body);
    this.physics.world.addConstraint(this.constraint);
    hitEl.emit('grabbed');
    scene = this.el.sceneEl;
    scene.grabbingControllers++;

    // Make linkers directly affected by this move vanish
    vanishLinkers(this);

    domains = document.querySelectorAll('.domain').length;
    domainsForStr = domains - 1;
    linkers = document.querySelectorAll('.linker').length;
    linkersForStr = linkers - 1;
    scene = document.getElementById('scene');
    shift = scene.shift;
    leftover = linkers - shift - domains;

    // if holding the first domain, check for leading linker and make it vanish
    if(hitEl.id == 'dom0' && shift == 1){
      linker = document.getElementById('link0');
      linker.setAttribute('obj-model', 'obj', '../../media/empty.obj');
      linker.setAttribute('obj-model', 'mtl', '../../media/empty.mtl');
    }
    // if holding the last domain, check for trailing linker and make it vanish
    // if leftover is 0 it means there is an trailing linker
    if(hitEl.id == 'dom' + domainsForStr && leftover == 0){
      linker = document.getElementById('link' + linkersForStr);
      linker.setAttribute('obj-model', 'obj', '../../media/empty.obj');
      linker.setAttribute('obj-model', 'mtl', '../../media/empty.mtl');
    }
  },
  
 tick: function(){
  // the line is updated to point between the two domains as they're moved around
    if(this.holding == true){
      lines = this.lines;
      for(var i=0; i<lines.length; i++){
        line = document.getElementById('line' + lines[i][0]);
        startbox = line.getAttribute('startbox');
        endbox = line.getAttribute('endbox');
        startbox = document.getElementById(startbox);
        endbox = document.getElementById(endbox);

        // use the line's startbox to get cartesian coordinates for its start position
        startboxMatrix = startbox.object3D.matrixWorld;
        var sPos = new THREE.Vector3;
        var sQuat = new THREE.Quaternion;
        var sScale = new THREE.Vector3;
        startboxMatrix.decompose(sPos, sQuat, sScale);
        sPos = "" + sPos['x'] + " " + sPos['y'] + " " + sPos['z'] + "";

        // use the line's endbox to get cartesian coordinates for its end position
        endboxMatrix = endbox.object3D.matrixWorld;
        var ePos = new THREE.Vector3;
        var eQuat = new THREE.Quaternion;
        var eScale = new THREE.Vector3;
        endboxMatrix.decompose(ePos, eQuat, eScale);
        ePos = "" + ePos['x'] + " " + ePos['y'] + " " + ePos['z'] + "";

        line.setAttribute('line', 'start: ' + sPos + '; end: ' + ePos + '; color: #00ff00');
      }
    }
  }
});