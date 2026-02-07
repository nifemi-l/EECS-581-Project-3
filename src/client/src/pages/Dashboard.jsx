// Prologue
// Name: dashboard.jsx
// Description: Define the dashboard page of our application and its functionality
// Programmers: Nifemi Lawal, Blake Carlson, Jack Bauer
// Creation date: 10/24/25
// Last revision date: 12/03/25
// Revisions: 1.4
// Pre/post conditions
//   - Pre: None.
//   - Post: None.
// Errors: None.

// Import statements for the temporary drawer -------------
import Drawer from '@mui/material/Drawer';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import TempDrawer from './TempDrawer.jsx';
// -----------------------------------------------------

// Dashboard page (Dashboard.jsx)
import React, { useState, useEffect, useRef, use } from 'react';
import LoaderBarsEffect from '../components/loading/LoaderBarsEffect';
import { Link } from 'react-router-dom';
import '../components/Metrics.css';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import FirstPage from '@mui/icons-material/FirstPage';
import LastPage from '@mui/icons-material/LastPage';
import '../components/Pagination.css';
import '../components/Tracks.css';
import '../components/SongOfTheDay.css';
import {useParams, Navigate} from 'react-router-dom'

export const server_address = `https://scorify-server.d3llie.tech`
export const client_address = `https://scorify.d3llie.tech`

async function refreshUserToken() {
  // Refresh the user`s token
  const response = await fetch(`${server_address}/refresh-user-token`, {
    credentials: `include`,
    mode: `cors`,
  });

  // Grab response code and message
  const responseCode = response.status;
  const data = await response.json();
  const responseMessage = data.error || data.message || `Unknown error`;

  // Return response code and message
  return [responseCode, responseMessage];
}

// Function to retrieve user information frome the backend API
// - Should not block the main thread
async function fetchUserInfo() {
  try {
    // Send GET request to backend API to get user information
    const response = await fetch(`${server_address}/get-user-info`, {
      credentials: `include`,
      mode: `cors`,
    });
    const updateDivScore = await fetch(`${server_address}/get-user-diversity-score`, {
      credentials: `include`,
      mode: `cors`,
    });

    const updateTasteScore = await fetch(`${server_address}/get-user-taste-score`, {
      credentials: `include`,
      mode: `cors`,
    });
    // Get response code from response
    const responseCode = response.status;
    // Jsonify response from backend API
    const data = await response.json();

    // OK response
    if (responseCode === 200) {
      return [
        {
          message: `User information successfully retrieved`,
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
        window.location.href = `${client_address}/login`;
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
      return [{ error: `Unknown error` }, responseCode];
    }
  } catch (error) {
    console.error(`Error fetching user information:`, error);
    return [{ error: `Error fetching user information` }, 500];
  }
}

async function fetchOtherUserInfo(user_id) {
  try {
    // Send GET request to backend API to get user information
    const response = await fetch(`${server_address}/get-user-info-by-id/${user_id}`, {
      credentials: `include`,
      mode: `cors`,
    });
    // Get response code from response
    const responseCode = response.status;
    // Jsonify response from backend API
    const data = await response.json();
    console.log(data)
    // OK response
    if (responseCode === 200) {
      return [
        {
          message: `User information successfully retrieved`,
          user_info: data.user_info
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
        window.location.href = `${client_address}/login`;
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
      return [{ error: `Unknown error` }, responseCode];
    }
  } catch (error) {
    console.error(`Error fetching user information:`, error);
    return [{ error: `Error fetching user information` }, 500];
  }
}

async function getUserListeningHistory(viewedUserId) {
  try {
    const response = await fetch(
      `${server_address}/get-user-listening-history-by-id/${viewedUserId}`,
      {
        credentials: `include`,
        mode: `cors`,
      },
    );
    // Get response code from response
    const responseCode = response.status;
    // Jsonify response from backend API
    const data = await response.json();
    console.log(data);

    // OK response
    if (responseCode === 200) {
      return [
        {
          message: `User listening history successfully retrieved`,
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
          return await getUserListeningHistory(viewedUserId);
        } else {
          return [{ error: refreshResponseErrorMessage }, refreshResponseCode];
        }
      } else {
        window.location.href = `${client_address}/login`;
        return [{ error: responseErrorMessage }, responseCode];
      }
    }
    // Unknown error response
    else {
      return [{ error: `Unknown error` }, responseCode];
    }
  } catch (error) {
    console.error(`Error fetching user listening history:`, error);
    return [{ error: `Error fetching user listening history` }, 500];
  }
}
// Function that fetches the listening history of a user given their stored internal id retrieved from url.
async function fetchUserListeningHistory(viewingId) {
  try {
    const response = await fetch(
      `${server_address}/fetch-user-listening-history-by-id/${viewingId}`,
      {
        credentials: `include`,
        mode: `cors`,
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
          message: `User listening history successfully retrieved`,
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
          return await fetchUserListeningHistory(viewingId);
        } else {
          return [{ error: refreshResponseErrorMessage }, refreshResponseCode];
        }
      } else {
        window.location.href = `${client_address}/login`;
        return [{ error: responseErrorMessage }, responseCode];
      }
    }
    // Unknown error response
    else {
      return [{ error: `Unknown error` }, responseCode];
    }
  } catch (error) {
    console.error(`Error fetching user listening history:`, error);
    return [{ error: `Error fetching user listening history` }, 500];
  }
}

// Function to retrieve user diversity score from the backend API
async function fetchUserDiversityScore(viewingId) {
  const response = await fetch(
    `${server_address}/get-user-diversity-score-by-id/${viewingId}`,
    {
      credentials: `include`,
      mode: `cors`,
    },
  );
  const data = await response.json();
  data.diversity_score = (data.diversity_score * 100).toFixed(2);
  return data.diversity_score;
}

// Function to retrieve user taste score from the backend API
async function fetchUserTasteScore(viewingSpotifyId) {
  const response = await fetch(
    `${server_address}/get-user-taste-score-by-id/${viewingSpotifyId}`,
    {
      credentials: `include`,
      mode: `cors`,
    },
  );
  const data = await response.json();
  data.taste_score = (data.taste_score * 100).toFixed(2);
  return data.taste_score;
}

// Function to fetch song of the day from the backend API
async function fetchSongOfTheDay() {
  try {
    const response = await fetch(
      `${server_address}/get-song-of-the-day`,
      {
        credentials: `include`,
        mode: `cors`,
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
          message: `Song of the day successfully retrieved`,
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
        window.location.href = `${client_address}/login`;
        return [{ error: responseErrorMessage }, responseCode];
      }
    }
    // Unknown error response
    else {
      return [{ error: `Unknown error` }, responseCode];
    }
  } catch (error) {
    console.error(`Error fetching song of the day:`, error);
    return [{ error: `Error fetching song of the day` }, 500];
  }
}


function calculateTracksPerPage() { }

function Dashboard() {
  // Set up state for user information and listening history
  const [userInfo, setUserInfo] = useState(null);
  const [userListeningHistory, setUserListeningHistory] = useState(null);
  const [songOfTheDay, setSongOfTheDay] = useState(null);

  // Get the id of the user who`s dashboard you are trying to view from the end of the url
  const { viewedUserId } = useParams();
  
  // State for drawer
  const [drawerOpen, setDrawerOpen] = useState(false);

  // State for diversity score
  const [diversityScore, setDiversityScore] = useState(null);

  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [tracksPerPage, setTracksPerPage] = useState(7);
  const [allowedPages, setAllowedPages] = useState(5); // This works with any value greater than or equal to 0, although is ideal at sizes >= 3
  const leadInPages = Math.floor(allowedPages / 2) + 1; // This is the number of pages before we begin centering page numbers

  // State that stores the username of the user that is currently logged in using OAuth 2.0
  const loggedInUsername = userInfo?.display_name ?? null;

  // Stores the info of the user who`s dashboard you are trying to view
  const [otherUserInfo, setOtherUserInfo] = useState({});
  // Determine if this is your own dashboard
  const isOwnDashboard = viewedUserId === loggedInUsername;

  // Stores the id if the user who is currently signed into Spotify
  const loggedInUserId = userInfo?.user_id ?? null;

  // Calculate tracks per page based on viewport height
  useEffect(() => {
    const calculateTracksPerPage = () => {
      // Reserved height: header (~100px) + title (~50px) + pagination (~80px) + padding/margins (~50px)
      const reservedHeight = 280;
      const availableHeight = window.innerHeight - reservedHeight;

      // Listening history takes up about 30% of the screen width
      const availableWidth = window.innerWidth * 0.3;

      // Each track card is approximately 85px (60px image + padding + gap) - made thinner
      const trackCardHeight = 85;

      // Width factor increases as screen width decreases
      // It is higher with a smaller screen width
      // Track card height should be higher with a small screen width
      let widthFactor = 4096 / (availableWidth) - 10;

      // Calculate the number of tracks
      const calculatedTracks = Math.floor(availableHeight / Math.max(trackCardHeight * widthFactor, 85));

      // Ensure at least 2 tracks, max 15
      const tracks = Math.max(2, Math.min(15, calculatedTracks));
      setTracksPerPage(tracks);
    };
    // Calculate on mount and resize
    calculateTracksPerPage();
    window.addEventListener(`resize`, calculateTracksPerPage);

    return () => window.removeEventListener(`resize`, calculateTracksPerPage);
  }, []);

  // Calculate pages of listening history based on viewport width
  useEffect(() => {
    const calculateNumPageButtons = () => {
      // Get window width in pixels
      const windowWidth = window.innerWidth;

      // Listening history takes up about 31% of the screen, and we want it a little smaller
      const availableWidth = windowWidth * 0.28;

      // Each page button takes up around 45px plus some padding
      // Remove the 4 buttons navigational buttons
      // Ensure that we don`t attempt negative buttons
      const numPagesDisplayed = Math.max(Math.floor(availableWidth / 45) - 4, 0);

      // Set the number of pages allowed
      setAllowedPages(numPagesDisplayed);
    };
    // Calculate on mount and resize
    calculateNumPageButtons();
    window.addEventListener(`resize`, calculateNumPageButtons);

    return () => window.removeEventListener(`resize`, calculateNumPageButtons);
  }, []);


  // State for whether the drawer is toggled or not.
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  // State for diversity score

  // State for taste score
  const [tasteScore, setTasteScore] = useState(null);
  
  // State to track if Song of the Day has finished loading
  const [sotdLoaded, setSotdLoaded] = useState(false);

  const [isFetchingHistory, setIsFetchingHistory] = useState(false);

  // Use ref to prevent duplicate fetches in React StrictMode (dev)
  const hasFetchedRef = useRef(false);

  const handleFetchListeningHistory = async () => {
    setIsFetchingHistory(true);
    const [fetchResponse, fetchCode] = await fetchUserListeningHistory(viewedUserId);

    if (fetchCode !== 200) {
      console.error(`Fetch failed:`, fetchResponse.error);
      setIsFetchingHistory(false);
      return;
    }

    if (fetchCode === 200) {
      // If we`ve sucessfully fetched listening history from Spotify, we need to check
      // if its different than what we currently have in the frontend and if so, update it.  
      let listening_history_len = fetchResponse[`user_listening_history`].length
      let listening_history_to_compare = []
      for (let i = 0; i < listening_history_len; i+= 1) {
        // We fetch much less listening history from spotify than we have in the database, so 
        // ensure that we only compare the recent data. 
        listening_history_to_compare.push(userListeningHistory[i])
      }
      let combinedListeningHistory = null

      // Iterate through both lists to see if the received listening history is the same
      // We`ll just make sure track name`s match, that should be sufficient. 
      let same = true;
      for (let i = 0; i < listening_history_len; i+= 1) {
        if (listening_history_to_compare[i].track_name !== fetchResponse[`user_listening_history`][i].track_name) {
          same = false; 
          console.log(`Failed at:`, i, listening_history_to_compare[i].track_name, fetchResponse[`user_listening_history`][i].track_name);
        }
      }

      // If listening histories between the new data from Spotify and what we already have are the same, then we keep everything the same.
      // Otherwise, we add the new data to our client`s internal listening history list while the database job runs in the background on the server.
      if (same) {
        console.log(`listening histories are equivalent`)
        combinedListeningHistory = userListeningHistory
      }
      else {
        console.log(`listening histories are NOT equivalent`)
        combinedListeningHistory = fetchResponse[`user_listening_history`].concat(userListeningHistory)
      }
      setUserListeningHistory(combinedListeningHistory);
      
    } else {
      // If we run into an error, say so
      console.error(
        `Failed to refresh listening history:`,
        fetchResponse.error,
      );
    }
    setIsFetchingHistory(false);
  };

  // Fetch user information and listening history concurrently when component mounts
  useEffect(() => {
    // Prevent double fetch in React StrictMode
    if (hasFetchedRef.current) {
      return;
    }

    const loadDashboardData = async () => {
      // Wait 700ms to ensure loader bars effect is visible
      await new Promise((resolve) => setTimeout(resolve, 700));
      
      try {
        // Fetch user info 
        const [userInfoResult] = await Promise.all([
          fetchUserInfo(),
        ]);

        const [otherResult, otherCode] = await fetchOtherUserInfo(viewedUserId);

        if (otherCode === 200) {
          const otherUser = otherResult.user_info[0];
          setOtherUserInfo(otherUser);
        }

        // Fetch listening history 
        // (we have to do this sequentially unfortunately since listening history depends on spotify_id)
        const [listeningHistoryResult] = await Promise.all([
          getUserListeningHistory(viewedUserId),
        ]);

        // Destructure results
        const [userInfoResponse, userInfoResponseCode] = userInfoResult;
        const [listeningHistoryResponse, listeningHistoryResponseCode] =
          listeningHistoryResult;

        if (userInfoResponseCode === 200) {
          setUserInfo(userInfoResponse[`user_info`]);
        } else {
          // If user info fetch fails, redirect to login
          window.location.href = `${client_address}/login`;
          return;
        }
        // Handle listening history response (can fail independently)
        if (listeningHistoryResponseCode === 200) {
          setUserListeningHistory(
            listeningHistoryResponse[`user_listening_history`],
          );
        } else {
          // Log error but don`t block dashboard since user info is more critical
          console.error(
            `Failed to fetch listening history:`,
            listeningHistoryResponse[`error`],
          );
          setUserListeningHistory([]); // Set empty array on failure
          setSongOfTheDay(null); // Set null when history fails
        }

        // Fetch diversity score
        try {
          const diversity = await fetchUserDiversityScore(viewedUserId);
          setDiversityScore(diversity);
        } catch (err) {
          console.error(`Failed to fetch diversity score:`, err);
          setDiversityScore(null);
        }

        // Fetch taste score
        try {
          const taste = await fetchUserTasteScore(viewedUserId);
          setTasteScore(taste);
        } catch (err) {
          console.error(`Failed to fetch taste score:`, err);
          setTasteScore(null);
        }

        // Fetch song of the day from backend
        try {
          const [songOfTheDayResult] = await Promise.all([
            fetchSongOfTheDay(),
          ]);
          const [songOfTheDayResponse, songOfTheDayResponseCode] = songOfTheDayResult;
          
          // Set song of the day on success and song of the day existing
          if (songOfTheDayResponseCode === 200 && songOfTheDayResponse.song_of_the_day) {
            setSongOfTheDay(songOfTheDayResponse.song_of_the_day);
            console.log(`Successfully fetched Song-of-the-Day from backend.`);
          } else {
            console.log(`No song of the day available or error occurred.`);
            setSongOfTheDay(null);
          }
        } catch (err) {
          console.error(`Failed to fetch song of the day:`, err);
          setSongOfTheDay(null);
        } finally {
          // Mark SOTD as loaded regardless of success/failure
          setSotdLoaded(true);
        }
      } catch (error) {
        console.error(`Error loading dashboard data:`, error);
        window.location.href = `${client_address}/login`;
      }
  }

    loadDashboardData();
  }, [isOwnDashboard, viewedUserId]);
  // Calculate indices for current page`s tracks
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

  // Reset to last page if we`re past the end of the array
  // This would occur if we`re at a high page number, and resizing lowers the amount of pages. 
  // If we go from 388 pages to 77 pages, then we need to update currentPage or we`d be out of bounds
  if (currentPage > totalPages) {
    setCurrentPage(totalPages);
  }

  // If user information or listening history is not loaded, show a loading message
  if (!userInfo || userListeningHistory === null || !sotdLoaded) {
    return <LoaderBarsEffect />;
  }
  
  // Redirect to own dashboard if no id is in the url or it is invalid and rerun the loading effect
  if (viewedUserId === null || viewedUserId === undefined || viewedUserId.length <= 0 || otherUserInfo.user_id === undefined) {
    return (
  <>
    <LoaderBarsEffect />
    <Navigate to={`/dashboard/${loggedInUserId}`} />
  </>
  );
}
  if (!isOwnDashboard && otherUserInfo.user_id === undefined) {
    return <LoaderBarsEffect />;
  }
  // Set ref to true to avoid duplicate fetches
  // hasFetchedRef.current = true;

  // If user information and listening history are loaded, show the dashboard
  // * Note: we need to wait for Song of the Day to load before showing the dashboard
  if (userInfo && userListeningHistory !== null && sotdLoaded) {
    return (
      <div id='dashboard-container'>
        <div className='header'>
          {/* Button toggling the temp drawer */}
          <IconButton onClick={toggleDrawer}>
            <MenuIcon fontSize='large' />
          </IconButton>
          <TempDrawer open={drawerOpen} onClose={toggleDrawer} />
          <div className='profile-container'>
            {/* Profile picture container */}
            <div className='profile-picture-container'>
              {/* Profile picture */}
              <div id='profile-picture'>
                {otherUserInfo.profile_image_url && otherUserInfo.profile_image_url.length > 0 ? (
                  <img src={otherUserInfo.profile_image_url} alt='Profile Picture' />
                ) : (
                  <svg
                    width='64'
                    height='64'
                    viewBox='0 0 24 24'
                    fill='currentColor'
                  >
                    <path d='M10.165 11.101a2.5 2.5 0 0 1-.67 3.766L5.5 17.173A3 3 0 0 0 4 19.771v.232h16.001v-.232a3 3 0 0 0-1.5-2.598l-3.995-2.306a2.5 2.5 0 0 1-.67-3.766l.521-.626.002-.002c.8-.955 1.303-1.987 1.375-3.19.041-.706-.088-1.433-.187-1.727a3.7 3.7 0 0 0-.768-1.334 3.767 3.767 0 0 0-5.557 0c-.34.37-.593.82-.768 1.334-.1.294-.228 1.021-.187 1.727.072 1.203.575 2.235 1.375 3.19l.002.002zm5.727.657-.52.624a.5.5 0 0 0 .134.753l3.995 2.306a5 5 0 0 1 2.5 4.33v2.232H2V19.77a5 5 0 0 1 2.5-4.33l3.995-2.306a.5.5 0 0 0 .134-.753l-.518-.622-.002-.002c-1-1.192-1.735-2.62-1.838-4.356-.056-.947.101-1.935.29-2.49A5.7 5.7 0 0 1 7.748 2.87a5.77 5.77 0 0 1 8.505 0 5.7 5.7 0 0 1 1.187 2.043c.189.554.346 1.542.29 2.489-.103 1.736-.838 3.163-1.837 4.355m-.001.001'></path>
                  </svg>
                )}
              </div>
            </div>

            {/* Display name container */}
            <div id='display-name-container'>
              {/* Display name */}
              <h1>{otherUserInfo.user_name}</h1>
            </div>
          </div>
        </div>

        <button
          id='fetch-listening-history'
          onClick={handleFetchListeningHistory}
        >
          Fetch listening history
        </button>

        {/* Dashboard Body */}
        <div id='dashboard-body'>
          {/* Metrics */}
          <div className='metrics-and-song-of-the-day'>
            {/* Song of the Day Banner - Contains album art, title, artist info, etc.*/}
            {songOfTheDay && (
              <div className='song-of-the-day-wrapper'>
                <p className='song-of-the-day-label'>🎵 Song of the Day</p>
                <div className='song-of-the-day-banner'>
                  {songOfTheDay.album_image && (
                    <img
                      src={songOfTheDay.album_image}
                      alt={songOfTheDay.track_name}
                      className='song-of-the-day-image'
                    />
                  )}
                  <div className='song-of-the-day-content'>
                    <h2 className='song-of-the-day-title'>
                      {songOfTheDay.spotify_url ? (
                        <a
                          href={songOfTheDay.spotify_url}
                          target='_blank'
                          rel='noopener noreferrer'
                        >
                          {songOfTheDay.track_name}
                        </a>
                      ) : (
                        songOfTheDay.track_name
                      )}
                    </h2>
                    <p className='song-of-the-day-artist'>
                      {songOfTheDay.artists}
                    </p>
                    {songOfTheDay.album_name && (
                      <p className='song-of-the-day-album'>
                        {songOfTheDay.album_name}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* This is the metrics section where we show the scores */}
            <div className='metrics'>
              <h1>Metrics</h1>
              <div className='metrics-container'>
                <div id='diversity-score' className='score'>
                  <h2>Diversity Score</h2>
                  <p className='score-value'>
                    {diversityScore !== null ? diversityScore : '...'}
                  </p>
                </div>
                <div id='taste-score' className='score'>
                  <h2>Music Taste Rating</h2>
                  <p className='score-value'>{tasteScore !== null ? `${tasteScore}` : '...'}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Dashboard content */}
          <div className='dashboard-content'>
            {isFetchingHistory && (
              <div className='loading-overlay'>
                <div className='spinner'></div>
              </div>
            )}
            {/* Display user listening history */}
            <h1>{otherUserInfo.user_name}'s Listening History</h1>
            {/* Make an array of track cards out of all our tracks. Each track displays some info such as its name, 
            the album art, and will link to the song on Spotify */}
            {currentTracks &&
              Array.isArray(currentTracks) &&
              currentTracks.length > 0 ? (
              <div className='tracks-list'>
                {currentTracks.map((track) => (
                  <div key={track.id} className='track-card'>
                    {track.album_image && (
                      <img
                        src={track.album_image}
                        alt={track.track_name}
                        className='album-art'
                      />
                    )}
                    <div className='track-info'>
                      <h3 className='track-name'>
                        {track.spotify_url ? (
                          <a
                            href={track.spotify_url}
                            target='_blank'
                            rel='noopener noreferrer'
                          >
                            {track.track_name}
                          </a>
                        ) : (
                          track.track_name
                        )}
                      </h3>
                      {/* Display the track artists as an array in case there are more than 1 */}
                      <p className='track-artists'>{
                        Array.isArray(track.artists) ? track.artists.join(', ') : track.artists}</p>
                    </div>
                  </div>
                ))}

                {/* Pagination buttons */}
                <div className='pagination-buttons'>
                  {/* There are four buttons aside from the main button list. 
                    - A previous button that resets to the first page
                    - A previous button that goes back one 
                    - (In between these two buttons is our variable-width button list of specific pages surrounding the current page)
                    - A next button that goes forward one
                    - A next button that goes to the last page
                  */}
                  <button
                    className='pagination-button previous-button'
                    onClick={() => {
                      if (currentPage > 1) {
                        setCurrentPage(1);
                      }
                    }}
                    disabled={currentPage <= 1}
                  >
                    <FirstPage />
                  </button>
                  <button
                    className='pagination-button previous-button'
                    onClick={() => {
                      if (currentPage > 1) {
                        setCurrentPage(currentPage - 1);
                      }
                    }}
                    disabled={currentPage <= 1}
                  >
                    <ChevronLeftIcon />
                  </button>
                  {/* 

                        The number of page options we display at the bottom of listening history is allowedPages.
                        The number of pages we need to pass through before centering the selected page is leadInPages. 
                        We handle four cases:
                          - Case 1: The current page is before leadInPages
                          - Case 2: The number of total pages is less than leadInPages (treated the same as case 1)
                          - Case 3: The current page is after totalPages - leadInPages (mostly same as case 2, but from the last page instead of the first)
                          - Case 4: We're in the middle. This is the most common case. The current page will be centered, and we will display Math.floor(allowedPages / 2) number of pages on either side. 

                        There are four aspects that need to keep consistent: 
                          - Active vs inactive (set the current page active)
                          - disabled (disable the current page)
                          - the actual number displayed on the page
                          - what page we click on when we click a button

                        All four aspects are generally the same, taking the appropriate action based on which case we're in. 
                        When considering each button, we first check if we're handling case 1 or case 2. If not, we check if we're handling case 3. If not, then we assume case 4.

                    */}
                  {Array.from({ length: allowedPages }, (_, index) => (
                    <button
                      key={index}
                      className={`pagination-button page-number-button page-number-${index + 1} ${(currentPage <= leadInPages || totalPages <= leadInPages ? currentPage === index + 1 : currentPage > totalPages - leadInPages ? currentPage === totalPages - allowedPages + index + 1 : index === Math.floor(allowedPages / 2)) ? 'active' : 'inactive'}`}
                      onClick={() => {
                        let toPage = currentPage <= leadInPages || totalPages <= leadInPages ? index + 1 : currentPage > totalPages - leadInPages ? index + 1 + totalPages - allowedPages : currentPage + (index - Math.floor(allowedPages / 2)); 
                        setCurrentPage(toPage)
                      }}
                      disabled={currentPage <= leadInPages || totalPages <= leadInPages ? currentPage === index + 1 : currentPage > totalPages - leadInPages ? totalPages - allowedPages + index + 1 === currentPage : index === Math.floor(allowedPages / 2)}
                    >
                      {currentPage <= leadInPages || totalPages <= leadInPages ? index + 1 : currentPage > totalPages - leadInPages ? index + 1 + totalPages - allowedPages : currentPage - Math.floor(allowedPages / 2) + index}
                    </button>
                  ))}
                  <button
                    className='pagination-button next-button'
                    onClick={() => {
                      if (currentPage < totalPages) {
                        setCurrentPage(currentPage + 1);
                      }
                    }}
                    disabled={currentPage >= totalPages}
                  >
                    <ChevronRightIcon />
                  </button>
                  <button
                    className='pagination-button next-button'
                    onClick={() => {
                      setCurrentPage(totalPages);
                    }}
                    disabled={currentPage >= totalPages}
                  >
                    <LastPage />
                  </button>
                </div>
              </div>
            ) : {/* If we run into an issue with listening history, say that it's unavailable */} (
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
