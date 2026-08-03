import { useState } from "react";
import {
  Routes,
  Route
} from "react-router-dom";

import "./App.css";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import BlogCard from "./components/BlogCard";
import BlogDetails from "./components/pages/BlogDetails";
import About from "./components/pages/About";
import Contact from "./components/pages/Contact";
import Blogs from "./components/pages/Blogs";

function App() {

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [image, setImage] = useState(null);

  const [posts, setPosts] = useState([
    {
      title: "Learning React",
      content: "React helps developers build modern web applications.",
      image: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800"
    },
    {
      title: "Technology",
      content: "Technology is changing the world every day.",
      image: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800"
    },
    {
      title: "Programming",
      content: "Programming helps us build websites and software.",
      image: "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800"
    }
  ]);

  const [editIndex, setEditIndex] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  const addPost = () => {
    if (title.trim() === "" || content.trim() === "") {
      alert("Please fill all fields");
      return;
    }

    if (isEditing) {
      const updatedPosts = [...posts];

      updatedPosts[editIndex] = {
        title,
        content,
        image: image
          ? URL.createObjectURL(image)
          : updatedPosts[editIndex].image,
      };

      setPosts(updatedPosts);
      setEditIndex(null);
      setIsEditing(false);

    } else {

      const newPost = {
        title,
        content,
        image: image
          ? URL.createObjectURL(image)
          : "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800",
      };

      setPosts([newPost, ...posts]);
    }

    setTitle("");
    setContent("");
    setImage(null);

    document.getElementById("imageInput").value = "";
  };

  const deletePost = (index) => {
    const updatedPosts = posts.filter((_, i) => i !== index);
    setPosts(updatedPosts);
  };

  return (
    <Routes>

      <Route path="/about" element={<About />} />

      <Route path="/blogs" element={<Blogs />} />

      <Route path="/contact" element={<Contact />} />

      <Route



        path="/"
        element={
          <>
            <Navbar />

            <section className="hero">
              <h1>Simple Blog Website</h1>
              <p>Create and share your own blog posts.</p>
            </section>
            <div className="blog-count">
              📚 Total Blogs: <strong>{posts.length}</strong>
            </div>

            <div className="blog-form">

              <h2>
                {isEditing ? "Edit Blog" : "Add New Blog"}
              </h2>

              <input
                type="text"
                placeholder="Enter Blog Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />

              <textarea
                placeholder="Write your blog..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />

              <input
                id="imageInput"
                type="file"
                accept="image/*"
                onChange={(e) => setImage(e.target.files[0])}
              />

              <button onClick={addPost}>
                {isEditing ? "Update Blog" : "Add Blog"}
              </button>

            </div>

            <div className="container">
              {posts.map((post, index) => (
                <BlogCard
                  key={index}
                  title={post.title}
                  description={post.content}
                  image={post.image}
                  onDelete={() => deletePost(index)}
                  onEdit={() => {
                    setTitle(post.title);
                    setContent(post.content);
                    setEditIndex(index);
                    setIsEditing(true);
                  }}
                  post={post}
                />
              ))}
            </div>

            <Footer />
          </>
        }
      />

      <Route
        path="/details"
        element={<BlogDetails />}
      />

    </Routes>
  );
}

export default App;


