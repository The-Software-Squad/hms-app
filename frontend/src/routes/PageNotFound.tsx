import pageNotFoundSVG from '../assets/404.svg';

export default function PageNotFound() {
	return (
		<div className='flex flex-col items-center justify-center h-screen p-32'>
			<img className='h-32' src={pageNotFoundSVG} alt="404 - Page Not Found" />
		</div>
	)
}
