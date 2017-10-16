/*
Helper functions called by the scripts written in viewer.html
*/

function changeLineColors(color, reset){
	/*
	Changes the color of the lines in the document. If reset is true, resets the line lengths as well
	@param color: the hex color to change the line color to
	@type color: string
	@param reset: whether or not to reset the line lengths
	@type reset: boolean
	*/
	var lines = document.querySelectorAll('.line');
	console.log(typeof lines)
	for(var i=0; i<lines.length; i++){
	  line = lines[i];
	  line.setAttribute('line', 'color', color);
	  if(reset == true){
	  	line.setAttribute('line', 'start', '0 0 0');
	  	line.setAttribute('line', 'end', '0 0 0');
	  }
	}
}

function setDomainPositions(domain_positions, hulls){
	/*
	Uses the domain positions given to set the domain elements' positions
	@param domain_positions: a list of all the domains' positions in aframe coordinates
	@type domain_positions: list
	@param hulls: whether to use hull colliders or not
	@type hulls: boolean
	*/

	scene = document.getElementById('scene');

	for(var i=0; i<domain_positions.length; i++){
	  position = JSON.parse(domain_positions[i]);
	// TODO: send dictionary instead, string slow {x:0, y:0, z:0} <- dict doesn't work!!
	  position_str = position[0] + " " + position[1] + " " + position[2];
	  // position_dict = {x: pos[0], y: pos[1], z: pos[2]};
	  piece = document.getElementById('dom' + i);
	  piece.setAttribute('position', position_str);
	  scene.domain_positions['dom' + i] = position;
	  if(hulls == 0){
	  	piece = document.getElementById('hull' + i);
	  	piece.setAttribute('position', position_str);
	  }
	}
}

function setLinkerPositions(linker_positions, change_linker){
	/*
	Uses the linker positions given to set the linker elements' positions
	@param linker_positions: a list of all the linkers' positions in aframe coordinates
	@type linker_positions: list
	@param change_linker: whether or not the linkers will be changed
	@type change_linker: boolean
	*/
	scene = document.getElementById('scene');
	temporary_directory = scene.temporary_directory;
	form_id = scene.form_id;
	version = scene.version;

	for(var i=0; i<linker_positions.length; i++){
	  position = JSON.parse(linker_positions[i]);
	  position_str = position[0] + " " + position[1] + " " + position[2];
	  piece = document.getElementById('link' + i);
	  piece.setAttribute('position', position_str);


	  /// TODO: HERE! PROBELM IS HERE! Now how to fix..
	  /// basically not accessing temporary directory files..

	  if(change_linker == true){
	  	console.log('try change model');
	  	console.log(window.location.pathname);
	  	piece.setAttribute('obj-model', 'obj', '/media/' + form_id + '/link' + i + '.' + version + '.obj');
	  	piece.setAttribute('obj-model', 'mtl', '/media/' + form_id + '/link' + i + '.' + version + '.mtl');
	  }
	}
}

function makeMatrices(pass){
	/*
	Creates transformation matrices from the domains' matrixWorlds and positions,
	edits them to match the input expected by biskit, then adds them to pass
	@param pass: holds the values that will be passed to aframeData.py in the ajax call
	@type pass: dictionary
	*/

  scene = document.getElementById('scene');
  domains = document.querySelectorAll('.domain');
  num = domains.length

  for(var i=0; i<num; i++){
  	// get the matrix describing each domain's new position and rotation
    position = domains[i].getAttribute('position');
    matrix = new THREE.Matrix4;
    quaternion = new THREE.Quaternion;
    elements = domains[i].object3D.matrixWorld.elements;

    elements[12] = elements[13] = elements[14] = 0;
    matrix.fromArray(elements);

    // find the change in position to apply avoid applying the transformation from the origin
    old_position = scene.domain_positions['dom' + i];

    delx = position['x'] - old_position[0];
    dely = position['y'] - old_position[1];
    delz = position['z'] - old_position[2];

    delta_position = {'x': delx, 'y': dely, 'z': delz};
    matrix.setPosition(delta_position);
    // transpose to match input expected by biskit
    matrix.transpose();
    matrix = matrix.elements.toString();

    pass['mat' + i] = matrix;
    scene.domain_positions['dom' + i] = [position['x'], position['y'], position['z']];
  
  }
}

function runRelative(data, change_linker){
	/*
	Runs the ajax call to renderRelative.
	@param data: holds the values that will be passed as the ajax call data
	@type data: dictionary
	@param change_linker: whether or not the linker's obj file needs to change
	@type change_linker: boolean
	*/
	$.ajax({
	  async: true,
	  type: 'POST',
	  url: "relative/",
	  data: data
	}).done(function(data){
	  scene = document.getElementById('scene');
	  hulls = scene.use_hulls;

	  presses = data[0];
	  domain_positions = data[1];
	  linker_positions = data[2]; 

	  // changes positions using the position data given in the response
	  if(change_linker == false){
	  	setDomainPositions(domain_positions, hulls);
	  	setLinkerPositions(linker_positions, false);
	  } else {
	  	// reset lines
	  	if(presses == scene.presses){
	  	  changeLineColors('#00ff00', true)
	  	  setLinkerPositions(linker_positions, true)

	  	  scene.loading = false;
	  	}
	  }
	});  
}