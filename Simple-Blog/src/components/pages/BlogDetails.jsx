import { Link, useLocation } from "react-router-dom";

function BlogDetails() {
  const location = useLocation();
  const post = location.state;

  if (!post) {
    return (
      <div style={{ textAlign: "center", marginTop: "50px" }}>
        <h2>No Blog Found</h2>
        <Link to="/">Go Back</Link>
      </div>
    );
  }

  return (
    <div className="details-container">
      <Link to="/" className="back-btn">
        ← Back to Home
      </Link>

      <img
        src={post.image}
        alt={post.title}
        className="details-image"
      />

      <h1>{post.title}</h1>

      <p className="details-content">
        {post.content}
      </p>
    </div>
  );
}

export default BlogDetails;