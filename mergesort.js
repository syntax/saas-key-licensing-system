function merge(left, right) {
    let array = []
    // Break out of loop if any one of the array gets empty
    while (left.length && right.length) {
        // Pick the smaller among the smallest element of left and right sub arrays
        if (left[0] < right[0]) {
            array.push(left.shift())
        } else {
            array.push(right.shift())
        }
    }

    // Concatenating the leftover elements
    // (in case we didn't go through the entire left or right array)
    // ... acts as a spread operator
    return [ ...array, ...left, ...right ]
}

function mergeSort(array) {
  const halflength = array.length / 2

  // Base case
  if(array.length < 2){
    return array
  }

  const left = array.splice(0, halflength)
  return merge(mergeSort(left),mergeSort(array))
}

//ONE WAY SORT
function sortTable2(col) {
    let table, rows, preswitch = [], switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("dbtable");
    rows = table.rows;
    let tbody = document.querySelector("#dbtable > tbody");
    let new_tbody = tbody.cloneNode();

    for (i = 1; i < (rows.length); i++) {
        preswitch.push(rows[i].getElementsByTagName("TD")[col].innerHTML)
    }
    //copy of preswitch
    let preswitch_copy = [...preswitch];

    function merge(left, right) {
        let array = []
        // Break out of loop if any one of the array gets empty
        while (left.length && right.length) {
            // Pick the smaller among the smallest element of left and right sub arrays
            if (left[0] < right[0]) {
                array.push(left.shift())
            } else {
                array.push(right.shift())
            }
        }

        // Concatenating the leftover elements
        // (in case we didn't go through the entire left or right array)
        // ... acts as a spread operator
        return [ ...array, ...left, ...right ]
    }

    function mergeSort(array) {
      const halflength = array.length / 2

      // Base case
      if(array.length < 2){
        return array
      }

      const left = array.splice(0, halflength)
      return merge(mergeSort(left),mergeSort(array))
    }

    sorted = mergeSort(preswitch);
    preswitch = preswitch_copy;
    console.log(preswitch);
    console.log(sorted);
    let index_array = [];
    // get the order of the sorted array based on the preswitch array
    sorted.forEach(value => {
        index_array.push(preswitch.indexOf(value));
        // console.log(index_array);
    })
    console.log(index_array);
    index_array.forEach(index => {
        // console.log(tbody.children[index].children[1].innerHTML);
        new_tbody.appendChild(tbody.children[index].cloneNode(true));
    })
    tbody.parentElement.replaceChild(new_tbody, tbody);
}

// TWO WAY SORT WITH UNDERLINE
function sortTable2(col) {
      //console.log(lastCol);
      //console.log(dir);
      if (lastCol == undefined) lastCol = col;
      if (dir == undefined) dir = "asc";
      if (lastCol != col) {
        dir = "asc";
        lastCol = col;
      }
      let table, rows, preswitch = [],
        switching, i, x, y, shouldSwitch, switchcount = 0;
      table = document.getElementById("dbtable");
      rows = table.rows;
      console.log(document.getElementsByTagName("TH"));
      for (heading of document.getElementsByTagName("TH")) {
      console.log(heading)
        heading.style.textDecoration = "none";
      }
      rows[0].getElementsByTagName("TH")[col].style.textDecoration = "underline";
      let tbody = document.querySelector("#dbtable > tbody");
      let new_tbody = tbody.cloneNode();
      //set direction to ascending initially
      if (dir == "asc") {
        dir = "desc"
      } else {
        dir = "asc"
      }

      for (i = 1; i < (rows.length); i++) {
        preswitch.push([rows[i].getElementsByTagName("TD")[0].innerHTML,rows[i].getElementsByTagName("TD")[col].innerHTML])
      }
      //copy of preswitch
      //console.log(preswitch)
      let preswitch_copy = [...preswitch];

      function merge(left, right) {
        let array = []
        // Break out of loop if any one of the array gets empty
        while (left.length && right.length) {
          // Pick the smaller among the smallest element of left and right sub arrays
          if (left[0][1] < right[0][1]) {
            array.push(left.shift())
          } else {
            array.push(right.shift())
          }
        }

        // Concatenating the leftover elements
        // (in case we didn't go through the entire left or right array)
        // ... acts as a spread operator
        return [...array, ...left, ...right]
      }

      function mergeSort(array) {
        const halflength = array.length / 2

        // Base case
        if (array.length < 2) {
          return array
        }

        const left = array.splice(0, halflength)
        return merge(mergeSort(left), mergeSort(array))
      }

      sorted = mergeSort(preswitch);
      preswitch = preswitch_copy;
      // console.log(preswitch);
      //console.log(sorted);
      let index_array = [];
      // get the order of the sorted array based on the preswitch array
      sorted.forEach(value => {
        index_array.push(preswitch.indexOf(value));
        // console.log(index_array);
      })
      //console.log(index_array);
      if(dir=="desc")index_array.reverse();
      index_array.forEach(index => {
        // console.log(tbody.children[index].children[1].innerHTML);
        new_tbody.appendChild(tbody.children[index].cloneNode(true));
      })
      tbody.parentElement.replaceChild(new_tbody, tbody);
    }