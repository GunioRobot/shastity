(ns org.scode.shastity.config
  (:require [clojure.string :as string]))

(def ^{:private true} *default-path* "~/.shastity/config")
(def ^{:private true} *config* (atom nil))

(defn- expand-home
  "Expand ~ to user.home, non-intelligently."
  [s]
  (string/replace s "~" (System/getProperty "user.home")))

(defn set-default-config-location
  "Set the default location of the configuration file. This is only meant to be set on
  early bootstrap or in unit tests; arbitrarly changing it during a shastity session
  is not supported."
  [default-path]
  (set! *default-path* default-path))

(defn default-config-location
  []
  "Returns the default location of the shastity configuration file."
  (expand-home @*default-path*))

(defn read-config
  []
  {}) ; TODO

(defn get
  "Get the currently active configuration."
  []
  (if-let [c @*config*]
    c
    (do
      (compare-and-set! *config* nil (read-config (default-config-location)))
      @*config*)))