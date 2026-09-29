export default function UserAvatar({ username, avatarData, size = 40 }) {
  return (
    <span className="user-avatar" style={{ width: size, height: size }}>
      {avatarData
        ? <img src={avatarData} alt={`Foto profil ${username || 'pengguna'}`} />
        : <span aria-hidden="true">{(username || 'F').charAt(0).toUpperCase()}</span>}
    </span>
  )
}
