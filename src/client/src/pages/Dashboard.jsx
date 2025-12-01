// Prologue
// Name: dashboard.jsx
// Description: Define the dashboard page of our application and its functionality
// Programmer: Nifemi Lawal
// Creation date: 10/24/25
// Last revision date: 11/20/25
// Revisions: 1.3
// Pre/post conditions
//   - Pre: None.
//   - Post: None.
// Errors: None.

// Import statements for the temporary drawer -------------
import Drawer from "@mui/material/Drawer";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import TempDrawer from "./TempDrawer.jsx";
// -----------------------------------------------------

// Dashboard page (Dashboard.jsx)
import React, { useState, useEffect, useRef } from "react";
import LoaderBarsEffect from "../components/loading/LoaderBarsEffect";
import { Link } from "react-router-dom";
import "../components/Metrics.css";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import "../components/Pagination.css";
import "../components/Tracks.css";
import "../components/SongOfTheDay.css";

async function refreshUserToken() {
  // Refresh the user's token
  const response = await fetch("http://127.0.0.1:5000/refresh-user-token", {
    credentials: "include",
    mode: "cors",
  });

  // Grab response code and message
  const responseCode = response.status;
  const data = await response.json();
  const responseMessage = data.error || data.message || "Unknown error";

  // Return response code and message
  return [responseCode, responseMessage];
}

// Function to retrieve user information frome the backend API
// - Should not block the main thread
async function fetchUserInfo() {
  try {
    // Send GET request to backend API to get user information
    const response = await fetch("http://127.0.0.1:5000/get-user-info", {
      credentials: "include",
      mode: "cors",
    });
    // Get response code from response
    const responseCode = response.status;
    // Jsonify response from backend API
    const data = await response.json();

    // OK response
    if (responseCode === 200) {
      return [
        {
          message: "User information successfully retrieved",
          user_info: data.user_info,
        },
        responseCode,
      ];
    }

    // Unauthorized response
    else if (responseCode === 401) {
      // Return error message and redirect to login
      const responseErrorMessage = data.error;
      const needsRefresh = data.needs_refresh;

      // If user token is expired, try to refresh
      if (needsRefresh === true) {
        const [refreshResponseCode, refreshResponseErrorMessage] =
          await refreshUserToken();
        if (refreshResponseCode === 200) {
          // Retry the original request with the new token
          return await fetchUserInfo();
        } else {
          return [{ error: refreshResponseErrorMessage }, refreshResponseCode];
        }
      } else {
        window.location.href = "http://127.0.0.1:3000/login";
        return [
          {
            error: responseErrorMessage,
          },
          responseCode,
        ];
      }
    }
    // Unknown error response
    else {
      return [{ error: "Unknown error" }, responseCode];
    }
  } catch (error) {
    console.error("Error fetching user information:", error);
    return [{ error: "Error fetching user information" }, 500];
  }
}

async function getUserListeningHistory() {
  try {
    const response = await fetch(
      "http://127.0.0.1:5000/get-user-listening-history",
      {
        credentials: "include",
        mode: "cors",
      },
    );

    // Get response code from response
    const responseCode = response.status;
    // Jsonify response from backend API
    const data = await response.json();

    // OK response
    if (responseCode === 200) {
      return [
        {
          message: "User listening history successfully retrieved",
          user_listening_history: data.user_listening_history,
        },
        responseCode,
      ];
    }
    // Unauthorized response
    else if (responseCode === 401) {
      const responseErrorMessage = data.error;
      const needsRefresh = data.needs_refresh;

      // If user token is expired, try to refresh
      if (needsRefresh === true) {
        const [refreshResponseCode, refreshResponseErrorMessage] =
          await refreshUserToken();
        if (refreshResponseCode === 200) {
          // Retry the original request with the new token
          return await getUserListeningHistory();
        } else {
          return [{ error: refreshResponseErrorMessage }, refreshResponseCode];
        }
      } else {
        window.location.href = "http://127.0.0.1:3000/login";
        return [{ error: responseErrorMessage }, responseCode];
      }
    }
    // Unknown error response
    else {
      return [{ error: "Unknown error" }, responseCode];
    }
  } catch (error) {
    console.error("Error fetching user listening history:", error);
    return [{ error: "Error fetching user listening history" }, 500];
  }
}

async function fetchUserListeningHistory() {
  try {
    const response = await fetch(
      "http://127.0.0.1:5000/fetch-user-listening-history",
      {
        credentials: "include",
        mode: "cors",
      },
    );
    // Get response code from response
    const responseCode = response.status;
    // Jsonify response from backend API
    const data = await response.json();

    // OK response
    if (responseCode === 200) {
      return [
        {
          message: "User listening history successfully retrieved",
          user_listening_history: data.user_listening_history,
        },
        responseCode,
      ];
    }

    // Unauthorized response
    else if (responseCode === 401) {
      const responseErrorMessage = data.error;
      const needsRefresh = data.needs_refresh;

      // If user token is expired, try to refresh
      if (needsRefresh === true) {
        const [refreshResponseCode, refreshResponseErrorMessage] =
          await refreshUserToken();
        if (refreshResponseCode === 200) {
          // Retry the original request with the new token
          return await fetchUserListeningHistory();
        } else {
          return [{ error: refreshResponseErrorMessage }, refreshResponseCode];
        }
      } else {
        window.location.href = "http://127.0.0.1:3000/login";
        return [{ error: responseErrorMessage }, responseCode];
      }
    }
    // Unknown error response
    else {
      return [{ error: "Unknown error" }, responseCode];
    }
  } catch (error) {
    console.error("Error fetching user listening history:", error);
    return [{ error: "Error fetching user listening history" }, 500];
  }
}

// Function to retrieve user diversity score from the backend API
async function fetchUserDiversityScore() {
  const response = await fetch(
    "http://127.0.0.1:5000/get-user-diversity-score",
    {
      credentials: "include",
      mode: "cors",
    },
  );
  const data = await response.json();
  return data.diversity_score;
}

// Function to retrieve user taste score from the backend API
async function fetchUserTasteScore() {
  const response = await fetch(
    "http://127.0.0.1:5000/get-user-taste-score",
    {
      credentials: "include",
      mode: "cors",
    },
  );
  const data = await response.json();
  return data.taste_score;
}

// Function to fetch song of the day from the backend API
async function fetchSongOfTheDay() {
  try {
    const response = await fetch(
      "http://127.0.0.1:5000/get-song-of-the-day",
      {
        credentials: "include",
        mode: "cors",
      },
    );

    // Get response code from response
    const responseCode = response.status;
    // Jsonify response from backend API
    const data = await response.json();

    // OK response
    if (responseCode === 200) {
      return [
        {
          message: "Song of the day successfully retrieved",
          song_of_the_day: data.song_of_the_day,
        },
        responseCode,
      ];
    }
    // Unauthorized response
    else if (responseCode === 401) {
      const responseErrorMessage = data.error;
      const needsRefresh = data.needs_refresh;

      // If user token is expired, try to refresh
      if (needsRefresh === true) {
        const [refreshResponseCode, refreshResponseErrorMessage] =
          await refreshUserToken();
        if (refreshResponseCode === 200) {
          // Retry the original request with the new token
          return await fetchSongOfTheDay();
        } else {
          return [{ error: refreshResponseErrorMessage }, refreshResponseCode];
        }
      } else {
        window.location.href = "http://127.0.0.1:3000/login";
        return [{ error: responseErrorMessage }, responseCode];
      }
    }
    // Unknown error response
    else {
      return [{ error: "Unknown error" }, responseCode];
    }
  } catch (error) {
    console.error("Error fetching song of the day:", error);
    return [{ error: "Error fetching song of the day" }, 500];
  }
}

function calculateTracksPerPage() { }

function Dashboard() {
  // Set up state for user information and listening history
  const [userInfo, setUserInfo] = useState(null);
  const [userListeningHistory, setUserListeningHistory] = useState(null);
  const [songOfTheDay, setSongOfTheDay] = useState(null);

  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [tracksPerPage, setTracksPerPage] = useState(7);

  // Calculate tracks per page based on viewport height
  useEffect(() => {
    const calculateTracksPerPage = () => {
      // Reserved height: header (~100px) + title (~50px) + pagination (~80px) + padding/margins (~50px)
      const reservedHeight = 280;
      const availableHeight = window.innerHeight - reservedHeight;
      // Each track card is approximately 85px (60px image + padding + gap) - made thinner
      const trackCardHeight = 85;
      const calculatedTracks = Math.floor(availableHeight / trackCardHeight);
      // Ensure at least 2 tracks, max 15
      const tracks = Math.max(2, Math.min(15, calculatedTracks));
      setTracksPerPage(tracks);
    };

    // Calculate on mount and resize
    calculateTracksPerPage();
    window.addEventListener("resize", calculateTracksPerPage);

    return () => window.removeEventListener("resize", calculateTracksPerPage);
  }, []);

  // State for drawer
  const [drawerOpen, setDrawerOpen] = useState(false);

  // State for whether the drawer is toggled or not.
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  // State for diversity score
  const [diversityScore, setDiversityScore] = useState(null);

  // State for taste score
  const [tasteScore, setTasteScore] = useState(null);
  
  // State to track if Song of the Day has finished loading
  const [sotdLoaded, setSotdLoaded] = useState(false);

  // Use ref to prevent duplicate fetches in React StrictMode (dev)
  const hasFetchedRef = useRef(false);

  const handleFetchListeningHistory = async () => {
    const [fetchResponse, fetchCode] = await fetchUserListeningHistory();

    if (fetchCode !== 200) {
      console.error("Fetch failed:", fetchResponse.error);
      return;
    }

    if (fetchCode === 200) {
      setUserListeningHistory(fetchResponse['user_listening_history']);
    } else {
      console.error(
        "Failed to refresh listening history:",
        fetchResponse.error,
      );
    }
  };


  // Fetch user information and listening history concurrently when component mounts
  useEffect(() => {
    // Prevent double fetch in React StrictMode
    if (hasFetchedRef.current) {
      return;
    }
    hasFetchedRef.current = true;

    const loadDashboardData = async () => {
      // Wait 700ms to ensure loader bars effect is visible
      await new Promise((resolve) => setTimeout(resolve, 700));

      try {
        // Fetch user info 
        const [userInfoResult] = await Promise.all([
          fetchUserInfo(),
        ]);

        // Fetch listening history 
        // (we have to do this sequentially unfortunately since listening history depends on spotify_id)
        const [listeningHistoryResult] = await Promise.all([
          getUserListeningHistory(),
        ]);

        // Destructure results
        const [userInfoResponse, userInfoResponseCode] = userInfoResult;
        const [listeningHistoryResponse, listeningHistoryResponseCode] =
          listeningHistoryResult;

        if (userInfoResponseCode === 200) {
          setUserInfo(userInfoResponse["user_info"]);
        } else {
          // If user info fetch fails, redirect to login
          window.location.href = "http://127.0.0.1:3000/login";
          return;
        }
        // Handle listening history response (can fail independently)
        if (listeningHistoryResponseCode === 200) {
          setUserListeningHistory(
            listeningHistoryResponse["user_listening_history"],
          );
        } else {
          // Log error but don't block dashboard since user info is more critical
          console.error(
            "Failed to fetch listening history:",
            listeningHistoryResponse["error"],
          );
          setUserListeningHistory([]); // Set empty array on failure
          setSongOfTheDay(null); // Set null when history fails
        }

        // Fetch diversity score
        try {
          const diversity = await fetchUserDiversityScore();
          setDiversityScore(diversity);
        } catch (err) {
          console.error("Failed to fetch diversity score:", err);
          setDiversityScore(null);
        }

        // Fetch taste score
        try {
          const taste = await fetchUserTasteScore();
          setTasteScore(taste);
        } catch (err) {
          console.error("Failed to fetch taste score:", err);
          setTasteScore(null);
        }

        // Fetch song of the day from backend
        try {
          const [songOfTheDayResult] = await Promise.all([
            fetchSongOfTheDay(),
          ]);
          const [songOfTheDayResponse, songOfTheDayResponseCode] = songOfTheDayResult;
          
          if (songOfTheDayResponseCode === 200 && songOfTheDayResponse.song_of_the_day) {
            setSongOfTheDay(songOfTheDayResponse.song_of_the_day);
            console.log("Successfully fetched Song-of-the-Day from backend.");
          } else {
            console.log("No song of the day available or error occurred.");
            setSongOfTheDay(null);
          }
        } catch (err) {
          console.error("Failed to fetch song of the day:", err);
          setSongOfTheDay(null);
        } finally {
          // Mark SOTD as loaded regardless of success/failure
          setSotdLoaded(true);
        }
      } catch (error) {
        console.error("Error loading dashboard data:", error);
        window.location.href = "http://127.0.0.1:3000/login";
      }
    };

    loadDashboardData();
  }, []);

  // Calculate indices for current page's tracks
  const lastTrackIndex = currentPage * tracksPerPage;
  const firstTrackIndex = lastTrackIndex - tracksPerPage;
  // Get current tracks for the current page
  const currentTracks =
    userListeningHistory && Array.isArray(userListeningHistory)
      ? userListeningHistory.slice(firstTrackIndex, lastTrackIndex)
      : [];
  const totalPages =
    userListeningHistory && Array.isArray(userListeningHistory)
      ? Math.ceil(userListeningHistory.length / tracksPerPage)
      : 1;

  // If user information or listening history is not loaded, show a loading message
  if (!userInfo || userListeningHistory === null || !sotdLoaded) {
    return <LoaderBarsEffect />;
  }

  // If user information and listening history are loaded, show the dashboard
  // * Note: we need to wait for Song of the Day to load before showing the dashboard
  if (userInfo && userListeningHistory !== null && sotdLoaded) {
    return (
      <div id="dashboard-container">
        <div className="header">
          {/* Button toggling the temp drawer */}
          <IconButton onClick={toggleDrawer}>
            <MenuIcon fontSize="large" />
          </IconButton>
          <TempDrawer open={drawerOpen} onClose={toggleDrawer} />
          <div className="profile-container">
            {/* Profile picture container */}
            <div className="profile-picture-container">
              {/* Profile picture */}
              <div id="profile-picture">
                {userInfo.images && userInfo.images.length > 0 ? (
                  <img src={userInfo.images[0].url} alt="Profile Picture" />
                ) : (
                  <svg
                    width="64"
                    height="64"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path d="M10.165 11.101a2.5 2.5 0 0 1-.67 3.766L5.5 17.173A3 3 0 0 0 4 19.771v.232h16.001v-.232a3 3 0 0 0-1.5-2.598l-3.995-2.306a2.5 2.5 0 0 1-.67-3.766l.521-.626.002-.002c.8-.955 1.303-1.987 1.375-3.19.041-.706-.088-1.433-.187-1.727a3.7 3.7 0 0 0-.768-1.334 3.767 3.767 0 0 0-5.557 0c-.34.37-.593.82-.768 1.334-.1.294-.228 1.021-.187 1.727.072 1.203.575 2.235 1.375 3.19l.002.002zm5.727.657-.52.624a.5.5 0 0 0 .134.753l3.995 2.306a5 5 0 0 1 2.5 4.33v2.232H2V19.77a5 5 0 0 1 2.5-4.33l3.995-2.306a.5.5 0 0 0 .134-.753l-.518-.622-.002-.002c-1-1.192-1.735-2.62-1.838-4.356-.056-.947.101-1.935.29-2.49A5.7 5.7 0 0 1 7.748 2.87a5.77 5.77 0 0 1 8.505 0 5.7 5.7 0 0 1 1.187 2.043c.189.554.346 1.542.29 2.489-.103 1.736-.838 3.163-1.837 4.355m-.001.001"></path>
                  </svg>
                )}
              </div>
            </div>

            {/* Display name container */}
            <div id="display-name-container">
              {/* Display name */}
              <h1>{userInfo.display_name}</h1>
            </div>
          </div>
        </div>

        <button
          id="fetch-listening-history"
          onClick={handleFetchListeningHistory}
        >
          Fetch listening history
        </button>

        {/* Dashboard Body */}
        <div id="dashboard-body">
          {/* Metrics */}
          <div className="metrics-and-song-of-the-day">
            {/* Song of the Day Banner */}
            {songOfTheDay && (
              <div className="song-of-the-day-wrapper">
                <p className="song-of-the-day-label">🎵 Song of the Day</p>
                <div className="song-of-the-day-banner">
                  {songOfTheDay.album_image && (
                    <img
                      src={songOfTheDay.album_image}
                      alt={songOfTheDay.track_name}
                      className="song-of-the-day-image"
                    />
                  )}
                  <div className="song-of-the-day-content">
                    <h2 className="song-of-the-day-title">
                      {songOfTheDay.spotify_url ? (
                        <a
                          href={songOfTheDay.spotify_url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {songOfTheDay.track_name}
                        </a>
                      ) : (
                        songOfTheDay.track_name
                      )}
                    </h2>
                    <p className="song-of-the-day-artist">
                      {songOfTheDay.artists}
                    </p>
                    {songOfTheDay.album_name && (
                      <p className="song-of-the-day-album">
                        {songOfTheDay.album_name}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div className="metrics">
              <h1>Metrics</h1>
              <div className="metrics-container">
                <div id="diversity-score" className="score">
                  <h2>Diversity Score</h2>
                  <p className="score-value">
                    {diversityScore !== null ? diversityScore : "..."}
                  </p>
                </div>
                <div id="taste-score" className="score">
                  <h2>Music Taste Rating</h2>
                  <p className="score-value">{tasteScore !== null ? `${tasteScore}` : "..."}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Dashboard content */}
          <div className="dashboard-content">
            <h1>Your Listening History</h1>
            {currentTracks &&
              Array.isArray(currentTracks) &&
              currentTracks.length > 0 ? (
              <div className="tracks-list">
                {currentTracks.map((track) => (
                  <div key={track.id} className="track-card">
                    {track.album_image && (
                      <img
                        src={track.album_image}
                        alt={track.track_name}
                        className="album-art"
                      />
                    )}
                    <div className="track-info">
                      <h3 className="track-name">
                        {track.spotify_url ? (
                          <a
                            href={track.spotify_url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {track.track_name}
                          </a>
                        ) : (
                          track.track_name
                        )}
                      </h3>
                      <p className="track-artists">{track.artists}</p>
                    </div>
                  </div>
                ))}

                {/* Pagination buttons */}
                <div className="pagination-buttons">
                  <button
                    className="pagination-button previous-button"
                    onClick={() => {
                      if (currentPage > 1) {
                        setCurrentPage(currentPage - 1);
                      }
                    }}
                    disabled={currentPage <= 1}
                  >
                    <ChevronLeftIcon />
                  </button>
                  {Array.from({ length: totalPages }, (_, index) => (
                    <button
                      key={index}
                      className={`pagination-button page-number-button page-number-${index + 1} ${currentPage === index + 1 ? "active" : "inactive"}`}
                      onClick={() => setCurrentPage(index + 1)}
                      disabled={currentPage === index + 1}
                    >
                      {index + 1}
                    </button>
                  ))}
                  <button
                    className="pagination-button next-button"
                    onClick={() => {
                      if (currentPage < totalPages) {
                        setCurrentPage(currentPage + 1);
                      }
                    }}
                    disabled={currentPage >= totalPages}
                  >
                    <ChevronRightIcon />
                  </button>
                </div>
              </div>
            ) : (
              <p>No listening history available yet.</p>
            )}
          </div>
        </div>
      </div>
    );
  }
}

// Make the Dashboard component available for use
export default Dashboard;
