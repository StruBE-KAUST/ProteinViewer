// TODO: call the functions in this script in the on-grab-release function so that we send the object's position & rotation data only when it's moved (to run through biskit/modeller) by calling sendNewPos();

function sendNewPos(){
  // TODO: remive these lines.
  // temporarily change positions for testing; 
  $("#mol0").attr('position', "-20 20 13");
  $("#mol1").attr('position', "30 27 45");

  var domains = document.querySelectorAll('.model');
  var num = domains.length;

  var matrices = {}

  for(var i=0; i<num; i++){
    pos = domains[i].getAttribute('position');
    rot = domains[i].getAttribute('rotation');
    mat = new THREE.Matrix4;
    mat.makeRotationFromEuler(rot);

    for(var j=0; j<16; j++){
      if(j==3){
        mat.elements[j] = pos['x'];
      } else if(j==7){
        mat.elements[j] = pos['y'];
      } else if(j==11){
        mat.elements[j] = pos['z'];
      }
    }

    mat = mat.elements.toString();
    matrices['mat' + i] = mat;
  }

  $.ajax({
    async: true,
    type: "POST",
    url: "return/",
    data: matrices
  }).done(function(msg) {
      console.log("Done");
      // maybe make call to modeller here? To use the newly produced pdbs? Or do we make modeller calls from python so it stays on the server side of things (like the call to vmd from views.py)? Probably better. If we run modeller from aframeData..? YES! Run modeller and get pdb for new linker, run that pdb through vmd, then load here..? Wait what. Okay yes we want to update this view when it completes, but how do we update only the linker's .obj&.mlt with the new ones? Cause after updating then we're finally done one "cycle"..  
  })
}