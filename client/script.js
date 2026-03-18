// script.js
const { createApp, ref, onMounted, toRaw, computed } = Vue;

createApp({
  setup() {
    const posts = ref([]);
    const loading = ref(true);
    const showModal = ref(false); 
    const newPostContent = ref(""); 
    const currentAccountId = ref(1); 
    const isSubmitting = ref(false);
    const allAccounts = ref([]);
    const currentView = ref('personal');

    const getActiveUsername = computed(() => {
      // Find the account object that matches the current ID
      const activeAcc = allAccounts.value.find(acc => acc.account_id === currentAccountId.value);
      
      // If it exists, return the handle; otherwise, return a placeholder
      return activeAcc ? activeAcc.handle : "Guest";
  });

    const isOwnProfile = computed(() => {
      return currentAccountId.value === targetAccountId.value;
    });

    const currentUserId = ref(1); // Hardcoded for Alice

    const searchQuery = ref('');
    const searchResults = ref([]);

    const handleSearch = async () => {
        if (searchQuery.value.length < 2) {
            searchResults.value = [];
            return;
        }
        
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/search?q=${searchQuery.value}`);
            searchResults.value = await response.json();
        } catch (e) {
            console.error("Search failed", e);
        }
    };

    const selectUser = (accountId) => {
        openProfile(accountId);
        searchQuery.value = '';
        searchResults.value = [];
    };

    const fetchAccounts = async () => {
        // URL now matches the new Flask route
        const response = await fetch(`http://127.0.0.1:5000/api/accounts/${currentUserId.value}`);
        allAccounts.value = await response.json();
        
        if (allAccounts.value.length > 0 && !currentAccountId.value) {
            currentAccountId.value = allAccounts.value[0].account_id;
        }
    };
    
    const handleAccountChange = async () => {
        if (currentAccountId.value === 'NEW_ACCOUNT') {
            const newName = prompt("Enter a name for your new account:");
            if (newName) {
                await createNewAccount(newName);
            } else {
                // Revert selection if cancelled
                currentAccountId.value = allAccounts.value[0]?.account_id;
            }
        } else {
            await fetchFeed();
        }
    };

    const handleFollow = async (post) => {
      try {
          const response = await fetch('http://127.0.0.1:5000/api/follow', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                  follower_id: currentAccountId.value, 
                  followed_id: post.account_id 
              })
          });
          const result = await response.json();
          
          if (result.success) {
              // Update all posts by this author in the current feed
              posts.value.forEach(p => {
                  if (p.account_id === post.account_id) {
                      p.is_followed = (result.status === 'followed');
                  }
              });
          }
      } catch (e) {
          console.error("Follow toggle failed", e);
      }
    };

    const handleFollowFromModal = async (profile) => {
      try {
          const response = await fetch('http://127.0.0.1:5000/api/follow', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                  follower_id: currentAccountId.value, 
                  followed_id: profile.account_id 
              })
          });
          const result = await response.json();
          
          if (result.success) {
              // Update the modal's local state
              profile.is_followed = (result.status === 'followed');
              
              // Sync the feed in the background so the buttons match
              posts.value.forEach(p => {
                  if (p.account_id === profile.account_id) {
                      p.is_followed = profile.is_followed;
                  }
              });
          }
      } catch (e) {
          console.error("Modal follow failed", e);
      }
  };

    const handleBlock = async (targetId) => {
      if (!confirm("Are you sure? You won't see their posts anymore.")) return;
      
      const response = await fetch('http://127.0.0.1:5000/api/block', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
              blocker_id: currentAccountId.value, 
              blocked_id: targetId 
          })
      });
      const result = await response.json();
      if (result.success) {
          showProfileModal.value = false;
          await fetchFeed(); // Refresh to hide their posts
      }
    };

    const handleDeletePost = async (postId) => {
      if (!confirm("Are you sure you want to delete this post?")) return;
  
      try {
          const response = await fetch(`http://127.0.0.1:5000/api/posts/${postId}`, {
              method: 'DELETE',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ account_id: currentAccountId.value })
          });
          const result = await response.json();
          if (result.success) {
              await fetchFeed(); // Refresh the feed to show it's gone
          }
      } catch (e) {
          console.error("Delete post failed", e);
      }
  };
  
  const handleDeleteComment = async (commentId, postId) => {
      try {
          const response = await fetch(`http://127.0.0.1:5000/api/comments/${commentId}`, {
              method: 'DELETE',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ account_id: currentAccountId.value })
          });
          const result = await response.json();
          if (result.success) {
              await fetchFeed();
          }
      } catch (e) {
          console.error("Delete comment failed", e);
      }
  };

  const handleEditPost = async (post) => {
    const newContent = prompt("Edit your post:", post.content);
    if (!newContent || newContent === post.content) return;

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/posts/${post.post_id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                account_id: currentAccountId.value, 
                content: newContent 
            })
        });
        const result = await response.json();
        if (result.success) {
            post.content = newContent; // Update UI instantly without a full reload
        }
    } catch (e) {
        console.error("Edit post failed", e);
    }
};

const handleEditComment = async (comment) => {
    const newContent = prompt("Edit your reply:", comment.content);
    if (!newContent || newContent === comment.content) return;

    try {
        const response = await fetch(`http://127.0.0.1:5000/api/comments/${comment.comment_id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                account_id: currentAccountId.value, 
                content: newContent 
            })
        });
        const result = await response.json();
        if (result.success) {
            comment.content = newContent;
        }
    } catch (e) {
        console.error("Edit comment failed", e);
    }
};

    const toggleLike = async (postId) => {
      await fetch(`http://127.0.0.1:5000/api/posts/${postId}/like`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ account_id: currentAccountId.value })
      });
      await fetchFeed(); // Refresh to see new like count
    };
  
    const submitComment = async (postId) => {
      const commentText = prompt("Write your reply:");
      if (!commentText || !commentText.trim()) return;
  
      try {
          const response = await fetch(`http://127.0.0.1:5000/api/posts/${postId}/comment`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                  account_id: currentAccountId.value,
                  content: commentText.trim() 
              })
          });
          
          const result = await response.json();
          
          if (result.success) {
              // Give the DB a split second to breathe, then refresh
              setTimeout(async () => {
                  await fetchFeed();
              }, 100); 
          } else {
              alert("Error posting comment: " + result.error);
          }
      } catch (error) {
          console.error("Failed to post comment:", error);
      }
    };

    const fetchCatchUp = async () => {
        loading.value = true;
        try {
            const response = await fetch('http://127.0.0.1:5000/api/catchup');
            posts.value = await response.json();
            currentView.value = 'trending'; // Update state to trending
        } finally {
            loading.value = false;
        }
    };
  
  const fetchGhosts = async () => {
      const response = await fetch(`http://127.0.0.1:5000/api/ghosts/${currentAccountId.value}`);
      const ghosts = await response.json();
      if (ghosts.length === 0) {
          alert("No ghost followers! Everyone is active.");
      } else {
          alert("Inactive followers: " + ghosts.map(g => g.username).join(", "));
      }
  };
  
  // Update this to match the team's new create_account logic
  const createNewAccount = async (handle) => {
      const response = await fetch('http://127.0.0.1:5000/api/accounts/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
              user_id: 1, // Alice
              username: handle // The backend route expects 'username' but saves it as 'handle'
          })
      });
      const result = await response.json();
      if (result.success) {
          await fetchAccounts();
          currentAccountId.value = result.account_id;
          await fetchFeed();
      }
  };
    
    const showProfileModal = ref(false);
    const profileData = ref({ bio: '', age: '', username: '' });

    const targetAccountId = ref(null);
    const accountActivity = ref([]);

    const openProfile = async (id) => {
      // 1. Determine which ID we are looking at
      const targetId = id || currentAccountId.value;
      targetAccountId.value = targetId; 
      
      try {
          // 2. Fetch profile info (Bio/Age)
          const profileRes = await fetch(`http://127.0.0.1:5000/api/users/${targetId}`);
          const profileInfo = await profileRes.json(); // Store this in a local variable first
          
          // 3. Fetch liked/commented activity
          const activityRes = await fetch(`http://127.0.0.1:5000/api/accounts/${targetId}/activity`);
          accountActivity.value = await activityRes.json();
  
          // 4. Check our existing feed to see if we already follow this person
          const knownPost = posts.value.find(p => p.account_id === targetId);
          
          // 5. Merge everything into profileData
          profileData.value = {
              ...profileInfo,        // Spread the bio/age/username from the API
              account_id: targetId,  // Use targetId here (not accountId)
              is_followed: knownPost ? knownPost.is_followed : false
          };
          
          showProfileModal.value = true;
      } catch (error) {
          console.error("Failed to load profile details:", error);
      }
  };

    const saveProfile = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:5000/api/profile/${currentAccountId.value}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    bio: profileData.value.bio,
                    age: profileData.value.age
                })
            });
            const result = await response.json();
            if (result.success) showProfileModal.value = false;
        } catch (error) {
            console.error("Save failed:", error);
        }
    };

    const fetchFeed = async () => {
      loading.value = true;
      currentView.value = 'personal';
      const id = currentAccountId.value;
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/feed/${id}`);
        
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}`);
        }
    
        const data = await response.json();
        posts.value = data;
      } catch (error) {
        console.error("CRITICAL ERROR:", error);
        posts.value = [{ 
            username: 'System', 
            content: '⚠️ Connection Error: Is your Flask server running?', 
            post_id: -1 
        }];
      } finally {
        loading.value = false; 
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString(undefined, { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    };

    const submitPost = async () => {
      isSubmitting.value = true;
      
      // Use a temporary constant to hold the number
      const idToSend = Number(currentAccountId.value);
      const contentToSend = String(newPostContent.value);
    
      console.log("Sending clean ID:", idToSend);
    
      try {
        const response = await fetch('http://127.0.0.1:5000/api/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            account_id: idToSend, // No objects, just the number
            content: contentToSend
          })
        });
        
        const result = await response.json();
        if (result.success) {
          newPostContent.value = "";
          showModal.value = false;
          await fetchFeed(); 
        } else {
          console.error("Flask Error:", result.error);
        }
      } catch (error) {
        console.error("Fetch Error:", error);
      } finally {
        isSubmitting.value = false;
      }
    };

    const getAvatarStyle = (username) => {
        if (!username) return 'background-color: #cbd5e1'; // Default gray
        
        // Generate a unique hash from the username
        let hash = 0;
        for (let i = 0; i < username.length; i++) {
            hash = username.charCodeAt(i) + ((hash << 5) - hash);
        }
        
        // Use HSL for vibrant, consistent colors (Saturation 70%, Lightness 60%)
        const hue = Math.abs(hash % 360);
        return `background-color: hsl(${hue}, 70%, 60%); color: white;`;
    };

    onMounted(async () => {
      // Run both calls. If fetchAccounts 404s, fetchFeed will still try to run.
      try {
          await fetchAccounts();
      } catch (e) {
          console.error("Account list failed to load (Check Flask route /api/accounts)");
      }
      
      await fetchFeed();
    });

    return {
        posts, 
        loading, 
        showModal, 
        newPostContent, 
        currentAccountId,
        allAccounts, 
        currentView,
        getActiveUsername, 
        isSubmitting,
        searchQuery,
        searchResults,
        handleSearch,
        selectUser,
        fetchFeed, 
        submitPost, 
        formatDate,
        openProfile,
        handleAccountChange,
        handleFollow,
        handleFollowFromModal,
        handleBlock,
        handleDeleteComment,
        handleDeletePost,
        handleEditComment,
        handleEditPost,
        accountActivity,
        showProfileModal,
        profileData,
        isOwnProfile,
        fetchCatchUp,
        fetchGhosts,
        saveProfile,
        toggleLike,
        submitComment,
        getAvatarStyle
    };
} // This was the missing setup brace!
}).mount('#app');