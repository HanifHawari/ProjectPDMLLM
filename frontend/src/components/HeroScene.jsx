import { useRef, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Sphere, MeshDistortMaterial, Ring, Float } from '@react-three/drei'
import * as THREE from 'three'

// Komponen untuk merender Bola 3D melayang dengan efek distorsi organik (cair/plasma)
function FloatingOrb({ position, color, speed, distort, scale }) {
  const meshRef = useRef()
  
  // Menganimasikan rotasi objek 3D berdasarkan waktu berjalan (elapsedTime)
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * speed * 0.3
      meshRef.current.rotation.y = state.clock.elapsedTime * speed * 0.5
    }
  })
  
  return (
    // Float membungkus bola agar bergoyang naik-turun secara alami
    <Float speed={1.2} rotationIntensity={0.4} floatIntensity={0.6}>
      <Sphere ref={meshRef} args={[scale, 64, 64]} position={position}>
        <MeshDistortMaterial
          color={color}
          distort={distort} // Nilai distorsi untuk membuat bola tidak bulat sempurna (efek cairan)
          speed={2} // Kecepatan gelombang distorsi
          roughness={0.15} // Tingkat kekasaran permukaan (makin kecil makin mengkilap/reflektif)
          metalness={0.6} // Efek logam/pantulan cahaya
          transparent
          opacity={0.75}
        />
      </Sphere>
    </Float>
  )
}

// Komponen untuk lintasan cincin orbit di sekitar bola utama
function RingOrbit({ radius, color, rotationSpeed }) {
  const ringRef = useRef()
  
  // Menggerakkan cincin dengan rotasi lambat pada sumbu X dan Z
  useFrame((state) => {
    if (ringRef.current) {
      ringRef.current.rotation.x = state.clock.elapsedTime * rotationSpeed * 0.2
      ringRef.current.rotation.z = state.clock.elapsedTime * rotationSpeed * 0.15
    }
  })
  
  return (
    <Ring ref={ringRef} args={[radius, radius + 0.03, 128]} rotation={[Math.PI / 3, 0.3, 0]}>
      <meshBasicMaterial color={color} transparent opacity={0.18} side={THREE.DoubleSide} />
    </Ring>
  )
}

export default function HeroScene() {
  return (
    // pointerEvents: 'none' agar scene 3D tidak menghalangi klik pada tombol di bawahnya
    <div style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}>
      <Canvas
        camera={{ position: [0, 0, 6], fov: 50 }}
        gl={{ alpha: true, antialias: true }} // alpha: true untuk latar belakang transparan
        style={{ background: 'transparent' }}
      >
        {/* Pencahayaan Ambient (merata ke seluruh objek) */}
        <ambientLight intensity={0.3} />
        
        {/* Pencahayaan Point (titik cahaya) hijau di kanan atas dan merah di kiri bawah */}
        <pointLight position={[4, 4, 4]} intensity={2} color="#22c55e" />
        <pointLight position={[-4, -2, 2]} intensity={1.5} color="#ef4444" />

        {/* Bola-bola 3D melayang dengan ukuran dan tingkat distorsi berbeda */}
        <FloatingOrb position={[1.8, 0.4, 0]} color="#22c55e" speed={0.4} distort={0.35} scale={1.1} />
        <FloatingOrb position={[-2.2, -0.3, -1]} color="#ef4444" speed={0.3} distort={0.25} scale={0.7} />
        <FloatingOrb position={[0, 0.8, -2]} color="#166534" speed={0.2} distort={0.2} scale={0.45} />

        {/* Lintasan cincin orbit transparan */}
        <RingOrbit radius={2.2} color="#22c55e" rotationSpeed={0.6} />
        <RingOrbit radius={3.0} color="#ef4444" rotationSpeed={0.4} />
      </Canvas>
    </div>
  )
}
