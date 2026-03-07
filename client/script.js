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

    const fetchAccounts = async () => {
        const response = await fetch('http://127.0.0.1:5000/api/accounts');
        allAccounts.value = await response.json();
    };

    const getActiveUsername = computed(() => {
        const active = allAccounts.value.find(a => a.account_id === currentAccountId.value);
        return active ? active.username : 'User';
    });

    const isOwnProfile = computed(() => {
      return currentAccountId.value === targetAccountId.value;
    });
    
    const showProfileModal = ref(false);
    const profileData = ref({ bio: '', age: '', username: '' });

    const targetAccountId = ref(null);

    const openProfile = async (id) => {
      // If no ID is passed (unlikely now), default to current user
      const targetId = id || currentAccountId.value;
      targetAccountId.value = targetId; 
      
      try {
          const response = await fetch(`http://127.0.0.1:5000/api/users/${targetId}`);
          const data = await response.json();
          // Fallback for bio/age if they are null in the DB
          profileData.value = {
              ...data,
              bio: data.bio || '',
              age: data.age || ''
          };
          showProfileModal.value = true;
      } catch (error) {
          console.error("Failed to load profile:", error);
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
      // ADD THESE NEW ENTRIES:
      openProfile,
      showProfileModal,
      profileData,
      isOwnProfile,
      saveProfile
    };
  } // This was the missing setup brace!
}).mount('#app');