addSugestionListener("start-location-input", "start-location-list");
addSugestionListener("target-location-input", "target-location-list");

document.addEventListener("DOMContentLoaded", function() {
    addSugestionListener("start-location-input", "start-location-list");
    addSugestionListener("target-location-input", "target-location-list");
  
    document.addEventListener("click", function(event) {
      const suggestionLists = document.querySelectorAll(".suggestions-list");
      
      suggestionLists.forEach(function(list) {
        const inputField = document.getElementById(list.id.replace("-list", "-input"));
        
        if (!inputField.contains(event.target) && !list.contains(event.target)) {
          list.innerHTML = "";
          list.classList.remove("show");
          list.style.pointerEvents = "none";
        }
      });
    });
  });

// Arrays to store all map elements
let routePolylines = [];
let routeMarkers = [];
let animationIntervals = []; 

// Function to clear the map
function clearMapRoutes() {
  routePolylines.forEach((polyline) => {
    polyline.setMap(null);
  });
  routePolylines = [];

  routeMarkers.forEach((marker) => {
    marker.setMap(null);
  });
  routeMarkers = [];

  animationIntervals.forEach((interval) => {
    clearInterval(interval);
  });
  animationIntervals = [];
}

function getLineColor(lineNumber) {
  const lineColors = {
    A: "#4361ee", 
    C: "#3a0ca3", 
    D: "#4cc9f0", 
    K: "#f72585", 
    N: "#7209b7", 
  };

  if (!isNaN(parseInt(lineNumber))) {
    const num = parseInt(lineNumber);
    const hue = 220 + ((num * 5) % 40); 
    const saturation = 70 + ((num * 3) % 20); 
    const lightness = 45 + ((num * 2) % 15); 
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  }

  if (lineColors[lineNumber]) {
    return lineColors[lineNumber];
  }

  return "#3b82f6";
}

function drawColoredRoute(stops, lineNumber, map) {
  if (stops.length < 2) return;

  const color = getLineColor(lineNumber);

  const path = stops.map((stop) => stop.location);

  const polyline = new google.maps.Polyline({
    path: path,
    geodesic: true,
    strokeColor: color,
    strokeOpacity: 0.9,
    strokeWeight: 5,
    map: map,
  });

  routePolylines.push(polyline);

  stops.forEach((stop, index) => {
    let markerIcon;
    let label = "";

    if (index === 0) {
      markerIcon = {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: "#10b981",
        fillOpacity: 1,
        strokeWeight: 2,
        strokeColor: "white",
        scale: 10,
      };
      label = {
        text: "A",
        color: "white",
        fontSize: "12px",
        fontWeight: "bold",
      };
    } else if (index === stops.length - 1) {
      markerIcon = {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: "#ef4444",
        fillOpacity: 1,
        strokeWeight: 2,
        strokeColor: "white",
        scale: 10,
      };
      label = {
        text: "B",
        color: "white",
        fontSize: "12px",
        fontWeight: "bold",
      };
    } else {
      markerIcon = {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: color,
        fillOpacity: 0.9,
        strokeWeight: 2,
        strokeColor: "white",
        scale: 7,
      };
    }

    const marker = new google.maps.Marker({
      position: stop.location,
      map: map,
      icon: markerIcon,
      title: stop.name,
      label: label,
      zIndex: index === 0 || index === stops.length - 1 ? 100 : 50,
    });

    const infoWindow = new google.maps.InfoWindow({
      content: `<div style="font-family: 'Inter', sans-serif; padding: 10px; min-width: 150px;">
                    <div style="font-weight: 600; font-size: 14px; margin-bottom: 5px;">${
                      stop.name
                    }</div>
                    ${
                      index > 0 && index < stops.length - 1
                        ? `<div style="display: inline-block; background-color: ${color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-top: 5px;">Linia ${lineNumber}</div>`
                        : index === 0
                        ? '<div style="font-size: 12px; color: #10b981; margin-top: 5px;"><i class="fas fa-circle"></i> Przystanek początkowy</div>'
                        : '<div style="font-size: 12px; color: #ef4444; margin-top: 5px;"><i class="fas fa-circle"></i> Przystanek końcowy</div>'
                    }
                  </div>`,
      maxWidth: 200,
      pixelOffset: new google.maps.Size(0, 0),
    });

    marker.addListener("click", function () {
      infoWindow.open(map, marker);
    });

    routeMarkers.push(marker);
  });


  if (stops.length >= 3) {
    try {
      animateRoute(polyline, color);
    } catch (error) {
      console.warn("Could not animate route:", error);
    }
  }

  return polyline;
}

function animateRoute(polyline, color) {
  const animatedIcon = {
    path: google.maps.SymbolPath.CIRCLE,
    fillColor: color || "#3b82f6",
    fillOpacity: 1,
    strokeWeight: 1,
    strokeColor: "white",
    scale: 6,
  };

  const animatedMarker = new google.maps.Marker({
    icon: animatedIcon,
    map: polyline.getMap(),
    zIndex: 200,
  });

  routeMarkers.push(animatedMarker);

  const path = polyline.getPath();
  const numPoints = path.getLength();

  if (numPoints < 2) {
    animatedMarker.setMap(null);
    return;
  }

  let currentIndex = 0;
  animatedMarker.setPosition(path.getAt(currentIndex));

  const animationInterval = setInterval(() => {
    currentIndex = (currentIndex + 1) % numPoints;
    animatedMarker.setPosition(path.getAt(currentIndex));

    if (currentIndex === 0) {
      animatedMarker.setMap(null);
      setTimeout(() => {
        animatedMarker.setMap(polyline.getMap());
      }, 1000);
    }
  }, 1000); 

  animationIntervals.push(animationInterval);
}

function displayRouteOnMap(routeData) {
  if (
    !routeData ||
    !routeData.route ||
    !Array.isArray(routeData.route) ||
    routeData.route.length === 0
  ) {
    console.error("No route data to display on map");
    return;
  }

  clearMapRoutes();

  const startLocation = document.getElementById("start-location-input").value;
  const endLocation = document.getElementById("target-location-input").value;

  console.log("Displaying route from", startLocation, "to", endLocation);

  const segmentsByLine = {};
  let previousStop = startLocation;

  routeData.route.forEach((segment, index) => {
    if (!segment.line || !segment.end_stop) return;

    const lineNumber = segment.line.toString();

    if (!segmentsByLine[lineNumber]) {
      segmentsByLine[lineNumber] = {
        stops: [previousStop],
        color: getLineColor(lineNumber),
      };
    }

    segmentsByLine[lineNumber].stops.push(segment.end_stop);
    previousStop = segment.end_stop;
  });

  const allStopNames = new Set();
  Object.values(segmentsByLine).forEach((line) => {
    line.stops.forEach((stop) => allStopNames.add(stop));
  });

  const geocoder = new google.maps.Geocoder();
  const stopArray = Array.from(allStopNames);
  const geocodingPromises = [];

  stopArray.forEach((stopName) => {
    const searchAddress = stopName + ", Wrocław, Polska";

    const promise = new Promise((resolve, reject) => {
      geocoder.geocode({ address: searchAddress }, (results, status) => {
        if (status === google.maps.GeocoderStatus.OK) {
          resolve({
            name: stopName,
            location: results[0].geometry.location,
          });
        } else {
          console.warn(`Could not find location for: ${stopName}`, status);
          reject(new Error(`Geocoding failed for: ${stopName}`));
        }
      });
    });

    geocodingPromises.push(promise);
  });

  Promise.all(geocodingPromises.map((p) => p.catch((e) => null)))
    .then((stops) => {
      const validStops = stops.filter((stop) => stop !== null);
      const stopsMap = {};

      validStops.forEach((stop) => {
        stopsMap[stop.name] = stop;
      });

      if (Object.keys(stopsMap).length < 2) {
        console.error("Not enough stops to draw a route on the map");
        return;
      }

      const bounds = new google.maps.LatLngBounds();
      validStops.forEach((stop) => bounds.extend(stop.location));

      Object.entries(segmentsByLine).forEach(([lineNumber, line]) => {
        const lineStops = line.stops
          .map((stopName) => stopsMap[stopName])
          .filter((stop) => stop !== undefined);

        if (lineStops.length >= 2) {
          drawColoredRoute(lineStops, lineNumber, map);
        }
      });

      map.fitBounds(bounds);

      if (validStops.length === 2) {
        map.setZoom(14);
      }
    })
    .catch((error) => {
      console.error("Error drawing route on map:", error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const submitBtn = document.getElementById("submit-btn");
  if (submitBtn) {
    submitBtn.addEventListener("click", handleSubmitButton);
  }

  const backBtn = document.getElementById("back-to-form");
  if (backBtn) {
    backBtn.addEventListener("click", function () {
      const simpleView = document.getElementById("simpleView");
      const resultsView = document.getElementById("results-view");

      resultsView.classList.remove("show");
      setTimeout(() => {
        resultsView.style.display = "none";
        simpleView.style.display = "block";
        setTimeout(() => {
          simpleView.style.opacity = "1";
        }, 50);
      }, 300);
    });
  }
});

function handleSubmitButton(event) {
  event.preventDefault(); 

  const source = document.getElementById("start-location-input");
  const target = document.getElementById("target-location-input");
  const time = document.getElementById("time-selector");
  const routesContainer = document.getElementById("routes-container");
  const loadingSplash = document.getElementById("loading-splash");

  let timeValue = time.value;
  if (timeValue && !timeValue.includes(":")) {
    timeValue += ":00"; 
  } else if (timeValue && timeValue.split(":").length === 2) {
    timeValue += ":00"; 
  }

  loadingSplash.classList.add("active");

  routesContainer.innerHTML = "";

  console.log(
    `Wysyłanie zapytania z parametrami: źródło=${source.value}, cel=${target.value}, czas=${timeValue}`
  );

  setTimeout(() => {
    fetch(`http://127.0.0.1:5000/api/shortest_path`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        source: source.value,
        target: target.value,
        time: timeValue, 
        num_routes: 5, 
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Odpowiedź API:", data);

        loadingSplash.classList.remove("active");

        const simpleView = document.getElementById("simpleView");
        const resultsView = document.getElementById("results-view");

        simpleView.style.opacity = "0";
        setTimeout(() => {
          simpleView.style.display = "none";
          resultsView.style.display = "block";
          setTimeout(() => {
            resultsView.classList.add("show");
          }, 50);
        }, 300);

        if (
          data.routes &&
          Array.isArray(data.routes) &&
          data.routes.length > 0
        ) {
          try {
            displayRouteOnMap(data.routes[0]);
          } catch (error) {
            console.error("Błąd podczas wyświetlania trasy na mapie:", error);
          }
        }

        if (
          data.routes &&
          Array.isArray(data.routes) &&
          data.routes.length > 0
        ) {
          let anyRouteDisplayed = false;

          data.routes.forEach((routeData) => {
            try {
              displayRoute(routeData, routesContainer);
              anyRouteDisplayed = true;
            } catch (error) {
              console.error("Błąd podczas wyświetlania trasy:", error);
            }
          });

          if (!anyRouteDisplayed) {
            routesContainer.innerHTML =
              '<div class="alert alert-warning">Nie udało się wyświetlić żadnej trasy</div>';
          }
        } else if (
          data.route &&
          Array.isArray(data.route) &&
          data.route.length > 0
        ) {
          try {
            displayRoute({ route: data.route }, routesContainer);
          } catch (error) {
            console.error("Błąd podczas wyświetlania trasy:", error);
            routesContainer.innerHTML =
              '<div class="alert alert-warning">Nie udało się wyświetlić trasy</div>';
          }
        } else {
          routesContainer.innerHTML =
            '<div class="alert alert-warning">Nie znaleziono tras</div>';
        }
      })
      .catch((error) => {
        loadingSplash.classList.remove("active");

        console.error("Error:", error);
        routesContainer.innerHTML = `<div class="alert alert-danger">Wystąpił błąd podczas wyszukiwania tras: ${error.message}</div>`;
      });
  }, 800); 

  console.log("Form submitted with time:", timeValue);
}

function displayRoute(routeData, container) {
  if (!routeData) {
    console.error("Błąd: routeData jest undefined lub null");
    throw new Error("Dane trasy są nieprawidłowe");
  }

  if (
    !routeData.route ||
    !Array.isArray(routeData.route) ||
    routeData.route.length === 0
  ) {
    console.error(
      "Błąd: route nie istnieje, nie jest tablicą lub jest pusta",
      routeData
    );
    throw new Error("Brak danych segmentów trasy");
  }

  const route = {
    departureTime: "", 
    arrivalTime: "", 
    segments: [],
  };

  const firstSegment = routeData.route[0];
  const lastSegment = routeData.route[routeData.route.length - 1];

  if (firstSegment && firstSegment.departure_time) {
    route.departureTime = firstSegment.departure_time.slice(0, 5); 
  } else {
    route.departureTime = "??:??";
    console.warn("Ostrzeżenie: Brak czasu odjazdu w pierwszym segmencie");
  }

  if (lastSegment && lastSegment.arrival_time) {
    route.arrivalTime = lastSegment.arrival_time.slice(0, 5);
  } else {
    route.arrivalTime = "??:??";
    console.warn("Ostrzeżenie: Brak czasu przyjazdu w ostatnim segmencie");
  }

  try {
    if (
      firstSegment &&
      firstSegment.departure_time &&
      lastSegment &&
      lastSegment.arrival_time
    ) {
      const startTime = new Date(`2023-01-01T${firstSegment.departure_time}`);
      const endTime = new Date(`2023-01-01T${lastSegment.arrival_time}`);
      const durationMs = endTime - startTime;
      const durationMinutes = Math.floor(durationMs / 60000);

      if (durationMinutes >= 60) {
        const hours = Math.floor(durationMinutes / 60);
        const minutes = durationMinutes % 60;
        route.duration = `${hours}h ${minutes}min`;
      } else {
        route.duration = `${durationMinutes} min`;
      }
    } else {
      route.duration = "? min";
    }
  } catch (error) {
    console.error("Błąd podczas obliczania czasu trwania podróży:", error);
    route.duration = "? min";
  }

  let currentLine = null;
  let currentSegment = null;

  routeData.route.forEach((item, index) => {
    if (!item || !item.line) {
      console.warn(`Segment #${index} ma brakujące dane:`, item);
      return; 
    }

    if (currentLine !== item.line || index === 0) {
      if (currentSegment) {
        route.segments.push(currentSegment);
      }

      let fromValue;
      if (index === 0) {
        fromValue = document.getElementById("start-location-input").value;
      } else if (
        routeData.route[index - 1] &&
        routeData.route[index - 1].end_stop
      ) {
        fromValue = routeData.route[index - 1].end_stop;
      } else {
        fromValue = "Nieznany przystanek";
      }

      let departureTime = "??:??";
      if (item.departure_time) {
        departureTime = item.departure_time.slice(0, 5);
      } else if (index === 0 && firstSegment && firstSegment.departure_time) {
        departureTime = firstSegment.departure_time.slice(0, 5);
      }

      let arrivalTime = "??:??";
      if (item.arrival_time) {
        arrivalTime = item.arrival_time.slice(0, 5);
      }

      currentSegment = {
        type: "bus",
        line: item.line.toString(),
        from: fromValue,
        to: item.end_stop || "Nieznany przystanek",
        time: `${departureTime} - ${arrivalTime}`,
      };

      currentLine = item.line;
    } else {
      currentSegment.to = item.end_stop || "Nieznany przystanek";

      if (item.arrival_time) {
        currentSegment.time = `${
          currentSegment.time.split(" - ")[0]
        } - ${item.arrival_time.slice(0, 5)}`;
      }
    }

    if (index === routeData.route.length - 1 && currentSegment) {
      route.segments.push(currentSegment);
    }
  });

  if (route.segments.length === 0) {
    console.error("Brak segmentów trasy po przetworzeniu danych");
    throw new Error("Nie można utworzyć segmentów trasy");
  }

  const finalSegments = [];
  for (let i = 0; i < route.segments.length; i++) {
    finalSegments.push(route.segments[i]);

    if (
      i < route.segments.length - 1 &&
      route.segments[i].to === route.segments[i + 1].from
    ) {
      try {
        const currentSegmentEnd = route.segments[i].time.split(" - ")[1];
        const nextSegmentStart = route.segments[i + 1].time.split(" - ")[0];

        if (currentSegmentEnd !== "??:??" && nextSegmentStart !== "??:??") {
          const endTime = new Date(`2023-01-01T${currentSegmentEnd}:00`);
          const startTime = new Date(`2023-01-01T${nextSegmentStart}:00`);
          const waitingMinutes = Math.floor((startTime - endTime) / 60000);

          if (waitingMinutes > 0) {
            finalSegments.push({
              type: "wait",
              duration: `${waitingMinutes} min`,
              from: route.segments[i].to,
              to: route.segments[i + 1].from,
            });
          }
        }
      } catch (error) {
        console.warn("Błąd podczas obliczania czasu oczekiwania:", error);
      }
    }
  }

  route.segments = finalSegments;

  const routeCard = document.createElement("div");
  routeCard.className = "route-card";

  let segmentsHTML = "";
  route.segments.forEach((segment) => {
    if (segment.type === "bus") {
      segmentsHTML += `
                  <div class="route-segment">
                      <div class="route-line bus-line">${segment.line}</div>
                      <div>
                          <div class="fw-bold">${segment.time}</div>
                          <div class="text-muted small">${segment.from} → ${segment.to}</div>
                      </div>
                  </div>
              `;
    } else if (segment.type === "wait") {
      segmentsHTML += `
                  <div class="route-segment">
                      <div class="route-line wait-segment"><i class="fas fa-clock"></i></div>
                      <div>
                          <div class="fw-bold">Czas oczekiwania (${segment.duration})</div>
                          <div class="text-muted small">Przystanek: ${segment.from}</div>
                      </div>
                  </div>
              `;
    }
  });

  routeCard.innerHTML = `
          <div class="route-card-header">
              <div class="route-time">
                  ${route.departureTime} - ${route.arrivalTime}
              </div>
              <div class="route-duration">
                  <i class="fas fa-clock me-1"></i> ${route.duration}
              </div>
          </div>
          <div class="route-details">
              ${segmentsHTML}
          </div>
      `;

  container.appendChild(routeCard);
  return true; 
}

function addSugestionListener(inputID, listID) {
    const inputField = document.getElementById(inputID);
    const suggestionsList = document.getElementById(listID);
  
    inputField.removeAttribute("data-valid-stop");
  
    suggestionsList.style.pointerEvents = "none";
  
    inputField.addEventListener("input", function() {
      const value = inputField.value.trim();
  
      inputField.removeAttribute("data-valid-stop");
      inputField.classList.remove("is-valid");
      inputField.classList.add("is-invalid");
  
      if (value.length >= 3) {
        fetch(`http://127.0.0.1:5000/api/suggestions?q=${encodeURIComponent(value)}`)
          .then(response => response.json())
          .then(data => {
            suggestionsList.innerHTML = "";
            showSuggestions(data, suggestionsList);
            
            suggestionsList.style.pointerEvents = "auto";
          })
          .catch(error => console.error("Błąd:", error));
      } else {
        suggestionsList.innerHTML = "";
        suggestionsList.classList.remove("show");
        suggestionsList.style.pointerEvents = "none";
      }
    });
  }

function showSuggestions(suggestions, list) {
  list.innerHTML = "";

  if (suggestions.length > 0) {
    suggestions.forEach(loc => {
      const item = document.createElement("li");
      item.className = "list-group-item";
      item.innerHTML = `
        <i class="fas fa-map-marker-alt"></i>
        <div>
          <div class="fw-bold">${loc}</div>
          <div class="text-muted small">Wrocław</div>
        </div>
      `;
      item.addEventListener("click", function() {
        const inputField = document.getElementById(list.id.replace("-list", "-input"));
        inputField.value = loc;

        inputField.setAttribute("data-valid-stop", "true");
        inputField.classList.add("is-valid");
        inputField.classList.remove("is-invalid");

        list.classList.remove("show");
        list.innerHTML = "";
        list.style.pointerEvents = "none";
      });
      list.appendChild(item);
    });
    list.classList.add("show");
  } else {
    list.classList.remove("show");
    list.style.pointerEvents = "none";
  }
}

function validateRouteForm() {
  const startInput = document.getElementById("start-location-input");
  const targetInput = document.getElementById("target-location-input");
  let isValid = true;

  if (!startInput.hasAttribute("data-valid-stop")) {
    startInput.classList.add("is-invalid");
    startInput.classList.remove("is-valid");
    let feedbackEl = document.querySelector(
      "#start-location-input + .invalid-feedback"
    );
    if (!feedbackEl) {
      feedbackEl = document.createElement("div");
      feedbackEl.className = "invalid-feedback";
      feedbackEl.textContent = "Wybierz przystanek z listy sugestii";
      startInput.parentNode.insertBefore(feedbackEl, startInput.nextSibling);
    }
    isValid = false;
  }

  if (!targetInput.hasAttribute("data-valid-stop")) {
    targetInput.classList.add("is-invalid");
    targetInput.classList.remove("is-valid");
    let feedbackEl = document.querySelector(
      "#target-location-input + .invalid-feedback"
    );
    if (!feedbackEl) {
      feedbackEl = document.createElement("div");
      feedbackEl.className = "invalid-feedback";
      feedbackEl.textContent = "Wybierz przystanek z listy sugestii";
      targetInput.parentNode.insertBefore(feedbackEl, targetInput.nextSibling);
    }
    isValid = false;
  }

  return isValid;
}

window.onload = function () {
  map = new google.maps.Map(document.getElementById("googleMapsContainer"), {
    center: { lat: 51.106, lng: 17.0258 },
    zoom: 13,
  });
};
