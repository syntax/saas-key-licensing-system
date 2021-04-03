if (typeof(Storage) !== "undefined") {
        if(localStorage.getItem("sidebar") == "opened"){
            document.querySelector("#mySidenav").style.width = "250px";
            document.querySelector("#main").style.marginLeft = "250px";
        }
    }
function openNav() {
  document.querySelector("#mySidenav").style.width = "250px";
  document.querySelector("#main").style.marginLeft = "250px";
  if (typeof(Storage) !== "undefined") {
        localStorage.setItem("sidebar", "opened");
    }
}
function closeNav() {
  document.querySelector("#mySidenav").style.width = "0";
  document.querySelector("#main").style.marginLeft = "0";
  if (typeof(Storage) !== "undefined") {
        localStorage.setItem("sidebar", "closed");
    }
}

var lastCol = undefined;
var dir = undefined;

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
  table = document.querySelector("#dbtable");
  rows = table.rows;
  console.log(document.querySelectorAll("TH"));
  for (heading of document.querySelectorAll("TH")) {
  console.log(heading)
    heading.style.textDecoration = "none";
  }
  rows[0].querySelectorAll("TH")[col].style.textDecoration = "underline";
  let tbody = document.querySelector("#dbtable > tbody");
  let new_tbody = tbody.cloneNode();
  //set direction to ascending initially
  if (dir == "asc") {
    dir = "desc"
  } else {
    dir = "asc"
  }

  for (i = 1; i < (rows.length); i++) {
    preswitch.push([rows[i].querySelectorAll("TD")[0].innerHTML,rows[i].querySelectorAll("TD")[col].innerHTML])
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