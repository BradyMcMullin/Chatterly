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

    const createNewAccount = async (username) => {
      try {
          const response = await fetch('http://127.0.0.1:5000/api/accounts/create', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                  user_id: 1, // Alice's hardcoded ID
                  username: username 
              })
          });
          const result = await response.json();
          if (result.success) {
              await fetchAccounts(); // Refresh list
              currentAccountId.value = result.account_id; // Switch to new account
              await fetchFeed();
          }
      } catch (error) {
          console.error("Failed to create account:", error);
      }
    };
    
    const showProfileModal = ref(false);
    const profileData = ref({ bio: '', age: '', username: '' });

    const targetAccountId = ref(null);
    const accountActivity = ref([]);

    const openProfile = async (id) => {
        const targetId = id || currentAccountId.value;
        targetAccountId.value = targetId; 
        
        try {
            // Fetch profile info (Bio/Age)
            const profileRes = await fetch(`http://127.0.0.1:5000/api/users/${targetId}`);
            profileData.value = await profileRes.json();
            
            // Fetch liked/commented activity
            const activityRes = await fetch(`http://127.0.0.1:5000/api/accounts/${targetId}/activity`);
            accountActivity.value = await activityRes.json();
            
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

    // 1. Fetch data from your Flask API
    const fetchFeed = async () => {
      loading.value = true;
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

    // 2. Formatting helper
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

    // 3. Submit a new post
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

    // Initialize
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
      getActiveUsername, 
      isSubmitting,
      fetchFeed, 
      submitPost, 
      formatDate,
      openProfile,
      handleAccountChange,
      accountActivity,
      showProfileModal,
      profileData,
      isOwnProfile,
      saveProfile,
      toggleLike,
      submitComment
    };
  } // This was the missing setup brace!
}).mount('#app');