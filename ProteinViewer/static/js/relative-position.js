function getRelativePos(){
  $.ajax({
    async: true,
    type: 'GET',
    url: "relative/",
    success: function(data){
      for(var i=0; i<data.length; i++){
        pos = JSON.parse(data[i]);
        // TODO: send dictionary instead, string slow {x:0, y:0, z:0} <- dict doesn't work!!
        posStr = pos[0] + " " + pos[1] + " " + pos[2];
        // posDict = {x: pos[0], y: pos[1], z: pos[2]};
        molID = "#mol" + i
        $(molID).attr('position', posStr);
      }

      // $("#mol0").attr('obj-model', 'obj: #model1; mtl: #mat1');
      // $("#mol1").attr('position', "0 0 0");
      // sendNewPos();
    }
  })
}