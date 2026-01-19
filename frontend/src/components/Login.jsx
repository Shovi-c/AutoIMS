import { Link, NavLink } from "react-router-dom";

const Login = () => {
  return (
    <div className="min-h-[90vh] w-full bg-stone-200 flex items-center justify-center p-6 caret-transparent ">
      <div className="w-full max-w-md bg-stone-300 rounded-2xl shadow-xl p-8 md:p-10">
        <div className="flex items-center   mb-6">
           <img src="/autoims.png" alt="AutoIMS Logo" className="w-16 h-16" />
          <span className="text-2xl font-bold text-gray-900">
            AutoIMS
          </span>
        </div>

        <p className="mt-1 text-sm text-gray-700 font-semibold">Manage your Services.</p>

        {/* Form */}
        <form className="mt-6 text-gray-700 space-y-4 ">
          <Input label="Email" type="email" placeholder="john@example.com" />
          <Input label="Password" type="password" placeholder="••••••••" />

          
          <div className="flex justify-center gap-4">
            <button
              type="button"
              className="w-full mt-2 rounded-full bg-indigo-700 py-3 text-sm font-semibold tracking-wide cursor-pointer text-white shadow-lg transition hover:-translate-y-0.5"
            >
              Login
            </button> 
          </div>
          <div className="text-right text-sm mt-2 text-indigo-700 font-medium cursor-pointer hover:underline">
            Forgot Password?
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-700 mt-4">
            <div className="flex-1 h-px bg-gray-400" />
            or
            <div className="flex-1 h-px bg-gray-400" />
          </div>
        </form>

        {/* Footer text-blue-600 font-semibold cursor-pointer */}
        <p className="mt-6 text-sm text-gray-700 text-center">
          Don’t have an account?{" "}
          <Link
            to="/Signup"
            className="text-indigo-700 font-semibold cursor-pointer hover:underline"
          >
            Create New!
          </Link>
        </p>
      </div>
    </div>
  );
};

const Input = ({ label, type = "text", placeholder }) => {
  return (
    <div className="select-text">
      <label className="block mb-1.5 text-xs font-semibold text-gray-500">
        {label}
      </label>
      <input
        type={type}
        placeholder={placeholder}
        autoComplete="off"
        className="
          w-full h-11 rounded-lg
          border border-blue-300
          px-4 text-sm text-gray-800
          outline-none transition
          focus:border-blue-500 focus:ring-2 focus:ring-blue-100
        "
      />
    </div>
  );
};

export default Login;
