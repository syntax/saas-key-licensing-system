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

function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("dbtable");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
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

// TWO WAY SORT
function sortTable2(col) {
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
      console.log(preswitch)
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
      console.log(sorted);
      preswitch = preswitch_copy;
      // console.log(preswitch);
      // console.log(sorted);
      let index_array = [];
      // get the order of the sorted array based on the preswitch array
      sorted.forEach(value => {
        index_array.push(preswitch.indexOf(value));
        // console.log(index_array);
      })
      console.log(index_array);
      if(dir=="desc")index_array.reverse();
      index_array.forEach(index => {
        // console.log(tbody.children[index].children[1].innerHTML);
        new_tbody.appendChild(tbody.children[index].cloneNode(true));
      })
      tbody.parentElement.replaceChild(new_tbody, tbody);
    }