'use client';

import Link from 'next/link';

export default function AdvertisingHome() {
  return (
    <div className='p-8'>
      <h1 className='text-4xl font-bold mb-4'>📣 Advertising Manager</h1>
      <p className='text-gray-600 mb-8'>Gestiona todas tus plataformas publicitarias</p>
      <div className='grid grid-cols-2 gap-4'>
        <Link href='/advertising/google-ads' className='p-6 border rounded hover:bg-gray-50'>
          <h3 className='font-bold text-lg'>🔍 Google Ads</h3>
        </Link>
        <Link href='/advertising/meta-ads' className='p-6 border rounded hover:bg-gray-50'>
          <h3 className='font-bold text-lg'>📱 Meta Ads</h3>
        </Link>
      </div>
    </div>
  );
}
