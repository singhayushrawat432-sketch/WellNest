import { Link } from "react-router-dom";

function BlogCard({
  title,
  description,
  image,
  onDelete,
  onEdit,
  post,
}) {
  return (
    <div className="card">
      <img
        src={image}
        alt={title}
        className="blog-image"
      />

      <div className="card-content">
        <h2>{title}</h2>

        <p>
          {description.length > 100
            ? description.substring(0, 100) + "..."
            : description}
        </p>

        <div className="button-group">
          <Link
            to="/details"
            state={post}
            className="view-btn"
          >
            View Details
          </Link>

          <button
            className="edit-btn"
            onClick={onEdit}
          >
            Edit
          </button>

          <button
            className="delete-btn"
            onClick={onDelete}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}

export default BlogCard;