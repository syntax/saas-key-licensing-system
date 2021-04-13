// following selections set sidebar to be open or closed in correspodnging with localstorage (from last page visited)

if (typeof(Storage) !== "undefined") {
        if(localStorage.getItem("sidebar") == "opened"){
            document.querySelector("#mySidenav").style.width = "250px";
            document.querySelector("#main").style.marginLeft = "250px";
        }
    }
function openNav() {
  // function for opening navigation panel, commits to local storage after change
  document.querySelector("#mySidenav").style.width = "250px";
  document.querySelector("#main").style.marginLeft = "250px";
  if (typeof(Storage) !== "undefined") {
        localStorage.setItem("sidebar", "opened");
    }
}
function closeNav() {
  // function for closing navigation panel, commits to local storage after change
  document.querySelector("#mySidenav").style.width = "0";
  document.querySelector("#main").style.marginLeft = "0";
  if (typeof(Storage) !== "undefined") {
        localStorage.setItem("sidebar", "closed");
    }
}

var lastCol = undefined;
var dir = undefined;

function sortTable2(col, isInteger = false) {
  // entire function has a time complexity of O(nlogn) due to merge sort being least time efficient sub function
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
  for (heading of document.querySelectorAll("TH")) {
    heading.style.textDecoration = "none";
  }
  // performs visual change, setting sorted column to be underlined
  rows[0].querySelectorAll("TH")[col].style.textDecoration = "underline";
  let tbody = document.querySelector("#dbtable > tbody");
  let new_tbody = tbody.cloneNode();
  //set direction to ascending initially
  if (dir == "asc") {
    dir = "desc"
  } else {
    dir = "asc"
  }
  // collects data from that column with its associated index number to be sorted
  if (isInteger) {
      for (i = 1; i < (rows.length); i++) {
        preswitch.push([rows[i].querySelectorAll("TD")[0].innerHTML,parseInt(rows[i].querySelectorAll("TD")[col].innerHTML)])
      }
  } else {
      for (i = 1; i < (rows.length); i++) {
        preswitch.push([rows[i].querySelectorAll("TD")[0].innerHTML,rows[i].querySelectorAll("TD")[col].innerHTML])
      }
  }
  //copy of preswitch
  let preswitch_copy = [...preswitch];

  function merge(left, right) {
    let array = []
    // in the case where any one of the arrays become empty, break out of the loop
    while (left.length && right.length) {
      // selects the smaller among the smallest element of the sub arrays (left and right)
      if (left[0][1] < right[0][1]) {
        array.push(left.shift())
      } else {
        array.push(right.shift())
      }
    }

    // concatenating the leftover elements
    // (in case we didn't go through the entire left or right array)
    // ... acts as a spread operator
    return [...array, ...left, ...right]
  }

  function mergeSort(array) {
  // performs the actual merge sort
    const halflength = array.length / 2

    // recursion base case
    if (array.length < 2) {
      return array
    }

    const left = array.splice(0, halflength)
    return merge(mergeSort(left), mergeSort(array))
  }

  sorted = mergeSort(preswitch);
  preswitch = preswitch_copy;
  let index_array = [];
  // get the order of the sorted array based on the preswitch array
  sorted.forEach(value => {
    index_array.push(preswitch.indexOf(value));
  })
  // simply reverses the array in the case it needs to be descending, to avoid having to merge sort again
  if(dir=="desc")index_array.reverse();
  index_array.forEach(index => {
    new_tbody.appendChild(tbody.children[index].cloneNode(true));
  })
  // performs visual change on the body of the table
  tbody.parentElement.replaceChild(new_tbody, tbody);
}