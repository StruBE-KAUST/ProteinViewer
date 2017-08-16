// TODO: call the functions in this script in the on-grab-release function so that we send the object's position & rotation data only when it's moved (to run through biskit/modeller) by calling sendNewPos();

function sendNewCoords(){

  ranges = {{ ranges }}

  domRanges = ranges[0]
  allRanges = ranges[1]

  var domains = document.querySelectorAll('.domain');
  console.log(domains);
  var num = domains.length;

  var matrices = {}

  for(var i=0; i<num; i++){
    id = domains[i].id
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

  var linkers = document.querySelectorAll('.linker');
  var numlinkers = linkers.length;

  inputs = [domRanges, allRanges, 'sequence.fasta']
  pass = [inputs, matrices]

  $.ajax({
    async: true,
    type: "POST",
    url: "return/",
    data: pass
  }).done(function(msg) {
    // TODO: once the new cordinates have been saved in a pdb, we need to 
    // run ranch/vmd/etc to get the new linker. Then use code below to place
    // the linker in the proper spot
    pieces = {'domains': 0, 'linkers': numlinkers}
    $.ajax({
      async: true,
      type: 'POST',
      url: "relative/",
      data: pieces
    }).done(function(data){
      linkers = data[1];
      for(var i=0; i<linkers.length; i++){
        pos = JSON.parse(linkers[i]);
        // TODO: send dictionary instead, string slow {x:0, y:0, z:0} <- dict doesn't work!!
        posStr = pos[0] + " " + pos[1] + " " + pos[2];
        // posDict = {x: pos[0], y: pos[1], z: pos[2]};
        molID = "#link" + i
        $(molID).attr('position', posStr);
      }
    });  
  })
}